"""Pre-quantum handoff assembly (chem layer; no orchestration imports)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.bridges.run_build_cache import RunBuildCache, pack_cache_key
from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    molecular_hamiltonian_from_canonical_active_space_pack,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from qchem_stack.chem.pre_quantum_input import PreQuantumInput, build_pre_quantum_meta
from qchem_stack.chem.pre_quantum_builder_registry import (
    get_pre_quantum_branch_builder,
    register_pre_quantum_branch_builder,
)
from qchem_stack.chem.pre_quantum_path import (
    PreQuantumPath,
    pre_quantum_path_source,
    resolve_pre_quantum_path,
)
from qchem_stack.chem.precomputed_pre_quantum import precomputed_pre_quantum_input
from qchem_stack.chem.pre_quantum_pyscf_gate import require_pyscf_reference  # re-exported API
from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import PipelineError

__all__ = [
    "build_pre_quantum_input",
    "build_pre_quantum_input_with_context",
    "hamiltonian",
    "hamiltonian_with_schmidt_context",
    "require_pyscf_reference",
    "schmidt_hamiltonian_and_context",
]


def schmidt_hamiltonian_and_context(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    *,
    backend_caps: Any | None = None,
) -> tuple[QubitHamiltonian, dict[str, Any]]:
    """Build primary Schmidt impurity ``QubitHamiltonian`` and context."""
    caps = backend_caps or create_solver(cfg).capabilities
    if not caps.supports_schmidt_atomic_hamiltonian:
        raise PipelineError(
            "embedding.dmet_hamiltonian_source='schmidt_atomic_production' requires backend support "
            f"(backend={caps.backend_id!r})."
        )
    require_pyscf_reference(rhf, context="schmidt_atomic_production")
    if cfg.scf.method != "RHF":
        raise PipelineError(
            "embedding.dmet_hamiltonian_source='schmidt_atomic_production' requires scf.method='RHF' "
            "(closed-shell single density matrix)."
        )
    from qchem_stack.chem.embedding.schmidt_production import (
        apply_chemical_potential_fragment_block,
        bisection_mu_for_fragment_electron_count,
        fci_fragment_ground_state,
        fragment_mulliken_electrons,
    )
    from qchem_stack.integrations.schmidt_dmet_self_consistent import (
        run_schmidt_density_feedback_cycles,
        run_schmidt_multifragment_density_cycles,
    )

    emb = cfg.embedding
    groups = emb.schmidt_multi_fragment_atom_groups
    if groups:
        labs = [x for x in emb.fragment_labels if str(x).strip()]
        model, dmet_loop_report, d_embed = run_schmidt_multifragment_density_cycles(
            rhf,
            fragment_atom_groups=[list(g) for g in groups],
            fragment_labels=labs if len(labs) == len(groups) else None,
            primary_fragment_index=int(emb.schmidt_multi_primary_fragment_index),
            n_bath_orbitals=int(emb.schmidt_n_bath_spatial),
            max_impurity_spatial_orbitals=int(emb.schmidt_max_impurity_spatial_orbitals),
            max_cycles=int(emb.schmidt_dmet_max_cycles),
            mixing_alpha=float(emb.schmidt_dmet_mixing_alpha),
            convergence_tol=float(emb.schmidt_dmet_convergence_tol),
        )
        multifrag_audit: dict[str, Any] = {
            "schmidt_multifragment": True,
            "n_embedding_fragments": len(groups),
            "primary_fragment_index": int(emb.schmidt_multi_primary_fragment_index),
        }
        schmidt_ctx: dict[str, Any] = {
            "D_embed": d_embed,
            "fragment_groups": [list(g) for g in groups],
            "fragment_labels": list(dmet_loop_report.get("fragment_labels_used", [])),
        }
    else:
        model, dmet_loop_report, d_embed = run_schmidt_density_feedback_cycles(
            rhf,
            fragment_atom_indices=list(emb.schmidt_fragment_atom_indices),
            n_bath_orbitals=int(emb.schmidt_n_bath_spatial),
            max_impurity_spatial_orbitals=int(emb.schmidt_max_impurity_spatial_orbitals),
            max_cycles=int(emb.schmidt_dmet_max_cycles),
            mixing_alpha=float(emb.schmidt_dmet_mixing_alpha),
            convergence_tol=float(emb.schmidt_dmet_convergence_tol),
        )
        multifrag_audit = {}
        schmidt_ctx = {
            "D_embed": d_embed,
            "fragment_groups": None,
            "fragment_labels": list(emb.fragment_labels) if emb.fragment_labels else ["fragment_0"],
        }

    mf = rhf.mf
    s = np.asarray(mf.get_ovlp(), dtype=float)
    frag_ao = list(model.meta.get("fragment_ao_indices", []))
    mulliken_frag = fragment_mulliken_electrons(d_embed, s, frag_ao)

    mu = 0.0
    mu_report: dict[str, Any] | None = None
    if emb.schmidt_run_mu_bisection and emb.dmet_target_fragment_electrons is not None:
        mu, mu_report = bisection_mu_for_fragment_electron_count(
            model,
            target_fragment_electrons=float(emb.dmet_target_fragment_electrons),
        )

    h1_use = apply_chemical_potential_fragment_block(
        model.h1, mu=mu, n_fragment_spatial_orbitals=model.n_fragment_spatial_orbitals
    )
    ne = model.n_alpha_electrons + model.n_beta_electrons

    fci_ref: dict[str, Any] | None = None
    if mu_report is not None:
        if mu_report.get("status") == "converged" and isinstance(mu_report.get("fci_at_mu"), dict):
            fci_ref = mu_report["fci_at_mu"]  # type: ignore[assignment]
        elif mu_report.get("status") == "no_bracket" and isinstance(
            mu_report.get("fci_mu_zero"), dict
        ):
            fci_ref = mu_report["fci_mu_zero"]  # type: ignore[assignment]
    elif emb.schmidt_attach_fci_reference and model.n_spatial_orbitals <= int(
        emb.schmidt_fci_reference_max_spatial_orbitals
    ):
        fci_ref = fci_fragment_ground_state(model, mu=mu)

    audit: dict[str, Any] = {
        "schema": "schmidt_production_pipeline_v1",
        "impurity_model": dict(model.meta),
        "schmidt_dmet_self_consistency": dmet_loop_report,
        "mulliken_fragment_after_embedding_density": mulliken_frag,
        "mu_on_fragment_diagonal_au": float(mu),
        "mu_bisection_report": mu_report,
        "fci_impurity_reference": fci_ref,
        "impurity_n_spatial_orbitals": model.n_spatial_orbitals,
        "impurity_n_electrons": int(ne),
        "active_space_yaml_ignored_for_qh": True,
        "note": (
            "Main variational stage uses impurity qubit Hamiltonian "
            f"({cfg.active_space.fermion_qubit_mapping}); cfg.active_space sizes apply to "
            "ledger/stub fields only on this path."
        ),
        **multifrag_audit,
    }
    qh = qubit_hamiltonian_from_spatial_chemist_integrals(
        model.constant,
        h1_use,
        model.h2,
        ne,
        fermion_qubit_mapping=cfg.active_space.fermion_qubit_mapping,
        integral_source="schmidt_impurity_spatial",
        meta_extra={"schmidt_production_audit": audit},
        pyscf_driver_meta=dict(rhf.driver_meta) if getattr(rhf, "driver_meta", None) else None,
    )
    return qh, schmidt_ctx


def _make_pre_quantum_input(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    qh: QubitHamiltonian,
    *,
    path: PreQuantumPath,
    pack: CanonicalActiveSpaceIntegralPack | None = None,
    meta_extra: dict[str, Any] | None = None,
) -> PreQuantumInput:
    source = pre_quantum_path_source(path)
    return PreQuantumInput(
        classical_reference=rhf,
        qubit_hamiltonian=qh,
        canonical_active_space_integral_pack=pack,
        meta=build_pre_quantum_meta(
            cfg,
            source=source,
            qubit_hamiltonian=qh,
            extra=meta_extra,
        ),
    )


def _build_pre_quantum_from_embedding_plugin(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None,
) -> tuple[PreQuantumInput, None]:
    from qchem_stack.chem.embedding.decomposition_plugin import (
        qubit_hamiltonian_from_decomposition_plugin,
    )

    qh = qubit_hamiltonian_from_decomposition_plugin(cfg, cfg_path=cfg_path)
    qh_meta = dict(getattr(qh, "meta", {}) or {})
    return (
        _make_pre_quantum_input(
            cfg,
            reference,
            qh,
            path=PreQuantumPath.EMBEDDING_PLUGIN,
            meta_extra={
                "decomposition_plugin": qh_meta.get("decomposition_plugin"),
                "decomposition_plugin_schema": qh_meta.get("decomposition_plugin_schema"),
            },
        ),
        None,
    )


def _build_pre_quantum_from_projection_fragment_mulliken(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    backend_caps: Any | None = None,
) -> tuple[PreQuantumInput, None]:
    caps = backend_caps or create_solver(cfg).capabilities
    if not caps.supports_projection_fragment_mulliken_hamiltonian:
        raise PipelineError(
            "projection.fragment_mulliken_mo requires backend support "
            f"(backend={caps.backend_id!r})."
        )
    from qchem_stack.chem.embedding.projection_hamiltonian import (
        molecular_hamiltonian_fragment_mulliken_projection,
    )

    qh, _audit = molecular_hamiltonian_fragment_mulliken_projection(reference, cfg)
    return (
        _make_pre_quantum_input(
            cfg,
            reference,
            qh,
            path=PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO,
        ),
        None,
    )


def _build_pre_quantum_from_canonical_pack(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cache: RunBuildCache | None,
    profile: Any | None,
    backend_caps: Any | None = None,
) -> tuple[PreQuantumInput, None]:
    caps = backend_caps or create_solver(cfg).capabilities
    if not caps.supports_restricted_active_space_qubit_hamiltonian:
        raise PipelineError(
            "This pipeline stage builds a qubit Hamiltonian from restricted active-space MO integrals; "
            f"the selected backend {caps.backend_id!r} does not provide "
            "a canonical active-space integral pack yet."
        )
    active = cfg.active_space
    na = int(active.n_active_orbitals)
    ne = int(active.n_active_electrons)

    def _build_pack() -> CanonicalActiveSpaceIntegralPack:
        return CanonicalActiveSpaceIntegralPack.from_classical_reference(
            reference,
            n_active_orbitals=na,
            n_active_electrons=ne,
        )

    if cache is not None:
        key = pack_cache_key(cfg, reference, n_active_orbitals=na, n_active_electrons=ne)
        pack = cache.get_or_build_pack(key, _build_pack)
    else:
        pack = _build_pack()

    if profile is not None:
        profile.mark("canonical_pack_ms")
    qh = molecular_hamiltonian_from_canonical_active_space_pack(
        pack,
        n_active_orbitals=active.n_active_orbitals,
        n_active_electrons=active.n_active_electrons,
        fermion_qubit_mapping=active.fermion_qubit_mapping,
        prefer_restricted_spatial_fermion_for_jordan_wigner=active.prefer_restricted_spatial_fermion_for_jordan_wigner,
        jordan_wigner_coeff_atol=active.jordan_wigner_coeff_atol,
        classical_reference_for_meta=reference,
    )
    if profile is not None:
        profile.mark("fermion_to_qubit_ms")
    return (
        _make_pre_quantum_input(
            cfg,
            reference,
            qh,
            path=PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK,
            pack=pack,
        ),
        None,
    )


def build_pre_quantum_input_with_context(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
    cache: RunBuildCache | None = None,
    profile: Any | None = None,
) -> tuple[PreQuantumInput, dict[str, Any] | None]:
    """Assemble :class:`PreQuantumInput` and optional Schmidt context for the sync pipeline."""
    _register_default_pre_quantum_branch_builders()
    path = resolve_pre_quantum_path(cfg)
    backend_caps = None
    if path in (
        PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION,
        PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO,
        PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK,
    ):
        backend_caps = create_solver(cfg).capabilities
    builder = get_pre_quantum_branch_builder(path)
    return builder(
        cfg,
        reference,
        cfg_path=cfg_path,
        cache=cache,
        profile=profile,
        backend_caps=backend_caps,
    )


def build_pre_quantum_input(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
    cache: RunBuildCache | None = None,
) -> PreQuantumInput:
    """Public chem entry: build :class:`PreQuantumInput` (same branches as the sync pipeline)."""
    pre_q, _ctx = build_pre_quantum_input_with_context(
        cfg, reference, cfg_path=cfg_path, cache=cache
    )
    return pre_q


def hamiltonian(cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference) -> QubitHamiltonian:
    return build_pre_quantum_input(cfg, rhf).qubit_hamiltonian


# Backward-compatible alias used by orchestration and tests.
hamiltonian_with_schmidt_context = build_pre_quantum_input_with_context


def _branch_precomputed_bundle(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
    **_kwargs: Any,
) -> tuple[PreQuantumInput, None]:
    return precomputed_pre_quantum_input(cfg, reference, cfg_path=cfg_path), None


def _branch_embedding_plugin(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
    **_kwargs: Any,
) -> tuple[PreQuantumInput, None]:
    return _build_pre_quantum_from_embedding_plugin(cfg, reference, cfg_path=cfg_path)


def _branch_schmidt_atomic_production(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    backend_caps: Any | None = None,
    **_kwargs: Any,
) -> tuple[PreQuantumInput, dict[str, Any] | None]:
    qh, ctx = schmidt_hamiltonian_and_context(cfg, reference, backend_caps=backend_caps)
    return _make_pre_quantum_input(cfg, reference, qh, path=PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION), ctx


def _branch_projection_fragment_mulliken(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    backend_caps: Any | None = None,
    **_kwargs: Any,
) -> tuple[PreQuantumInput, None]:
    return _build_pre_quantum_from_projection_fragment_mulliken(
        cfg,
        reference,
        backend_caps=backend_caps,
    )


def _branch_canonical_active_space_pack(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cache: RunBuildCache | None = None,
    profile: Any | None = None,
    backend_caps: Any | None = None,
    **_kwargs: Any,
) -> tuple[PreQuantumInput, None]:
    return _build_pre_quantum_from_canonical_pack(
        cfg,
        reference,
        cache=cache,
        profile=profile,
        backend_caps=backend_caps,
    )


_DEFAULT_BUILDERS_REGISTERED = False


def _register_default_pre_quantum_branch_builders() -> None:
    global _DEFAULT_BUILDERS_REGISTERED
    if _DEFAULT_BUILDERS_REGISTERED:
        return
    register_pre_quantum_branch_builder(
        PreQuantumPath.PRECOMPUTED_BUNDLE,
        _branch_precomputed_bundle,
        allow_override=True,
    )
    register_pre_quantum_branch_builder(
        PreQuantumPath.EMBEDDING_PLUGIN,
        _branch_embedding_plugin,
        allow_override=True,
    )
    register_pre_quantum_branch_builder(
        PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION,
        _branch_schmidt_atomic_production,
        allow_override=True,
    )
    register_pre_quantum_branch_builder(
        PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO,
        _branch_projection_fragment_mulliken,
        allow_override=True,
    )
    register_pre_quantum_branch_builder(
        PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK,
        _branch_canonical_active_space_pack,
        allow_override=True,
    )
    _DEFAULT_BUILDERS_REGISTERED = True

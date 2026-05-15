from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    molecular_hamiltonian_from_canonical_active_space_pack,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.scf_stage import solver_capabilities
from qchem_stack.quantum.algorithms.vqe import VQE


def require_pyscf_reference(
    rhf: ClassicalMeanFieldReference,
    *,
    context: str,
) -> Any:
    """Return a PySCF mean-field object only for still PySCF-specific branches."""
    tag = rhf.backend_tag()
    if tag != "pyscf":
        raise PipelineError(
            f"{context} currently requires PySCF-style mean-field handle (got backend={tag!r}). "
            "Use embedding.mode=plugin for backend-agnostic Hamiltonian ingestion, "
            "or implement the corresponding backend-specific bridge."
        )
    return rhf.as_pyscf_rhf_result()


def schmidt_hamiltonian_and_context(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference
) -> tuple[QubitHamiltonian, dict[str, Any]]:
    """Build primary Schmidt impurity ``QubitHamiltonian`` and context."""
    caps = solver_capabilities(cfg)
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
        resolved_labels = list(dmet_loop_report.get("fragment_labels_used", []))
        schmidt_ctx: dict[str, Any] = {
            "D_embed": d_embed,
            "fragment_groups": [list(g) for g in groups],
            "fragment_labels": resolved_labels,
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


def run_schmidt_per_fragment_vqe(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    schmidt_ctx: dict[str, Any],
    exe: Any,
) -> dict[str, Any] | None:
    """Independent VQE on each fragment impurity (post embedding density)."""
    groups = schmidt_ctx.get("fragment_groups")
    if not groups or len(groups) < 2:
        return None
    labels = schmidt_ctx.get("fragment_labels") or []
    if len(labels) != len(groups):
        return None
    if not cfg.embedding.schmidt_run_vqe_on_all_fragments:
        return None
    d = np.asarray(schmidt_ctx["D_embed"], dtype=float)
    emb = cfg.embedding
    from qchem_stack.chem.embedding.schmidt_production import build_schmidt_impurity_integrals

    mx = emb.schmidt_per_fragment_vqe_maxiter
    if mx is None:
        mx = cfg.quantum.vqe_maxiter
    rows: list[dict[str, Any]] = []
    require_pyscf_reference(rhf, context="schmidt_run_vqe_on_all_fragments")
    for i, atoms in enumerate(groups):
        model = build_schmidt_impurity_integrals(
            rhf,
            fragment_atom_indices=list(atoms),
            n_bath_orbitals=int(emb.schmidt_n_bath_spatial),
            max_impurity_spatial_orbitals=int(emb.schmidt_max_impurity_spatial_orbitals),
            density_ao=d,
        )
        ne = model.n_alpha_electrons + model.n_beta_electrons
        qh_i = qubit_hamiltonian_from_spatial_chemist_integrals(
            model.constant,
            model.h1,
            model.h2,
            ne,
            fermion_qubit_mapping=cfg.active_space.fermion_qubit_mapping,
            integral_source="schmidt_impurity_spatial_fragment",
            meta_extra={"fragment_id": labels[i]},
        )
        vr = VQE(qh_i, depth=cfg.quantum.vqe_depth, executor=exe).run(
            maxiter=int(mx),
            seed=int(cfg.random_seed) + i * 31,
        )
        rows.append(
            {
                "fragment_id": labels[i],
                "atom_indices": list(atoms),
                "energy": float(vr.energy),
                "nfev": int(vr.nfev),
                "n_qubits": int(qh_i.n_qubits),
            }
        )
    return {
        "schema": "schmidt_per_fragment_vqe_v1",
        "vqe_depth": cfg.quantum.vqe_depth,
        "vqe_maxiter_per_fragment": int(mx),
        "fragments": rows,
    }


def hamiltonian_with_schmidt_context(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
) -> tuple[PreQuantumInput, dict[str, Any] | None]:
    if cfg.embedding.mode == "plugin":
        from qchem_stack.chem.embedding.decomposition_plugin import (
            qubit_hamiltonian_from_decomposition_plugin,
        )

        qh = qubit_hamiltonian_from_decomposition_plugin(cfg, cfg_path=cfg_path)
        qh_meta = dict(getattr(qh, "meta", {}) or {})
        return (
            PreQuantumInput(
                classical_reference=rhf,
                qubit_hamiltonian=qh,
                canonical_active_space_integral_pack=None,
                meta={
                    "source": "embedding_plugin",
                    "integral_source": qh_meta.get("integral_source"),
                },
            ),
            None,
        )
    sol = create_solver(cfg)
    if cfg.embedding.dmet_hamiltonian_source == "schmidt_atomic_production":
        qh, ctx = schmidt_hamiltonian_and_context(cfg, rhf)
        return (
            PreQuantumInput(
                classical_reference=rhf,
                qubit_hamiltonian=qh,
                canonical_active_space_integral_pack=None,
                meta={"source": "schmidt_atomic_production"},
            ),
            ctx,
        )
    if (
        cfg.embedding.mode == "projection"
        and cfg.embedding.projection_quantum_hamiltonian == "fragment_mulliken_mo"
    ):
        if not sol.capabilities.supports_projection_fragment_mulliken_hamiltonian:
            raise PipelineError(
                "projection.fragment_mulliken_mo requires backend support "
                f"(backend={sol.capabilities.backend_id!r})."
            )
        from qchem_stack.chem.embedding.projection_hamiltonian import (
            molecular_hamiltonian_fragment_mulliken_projection,
        )

        qh, _audit = molecular_hamiltonian_fragment_mulliken_projection(rhf, cfg)
        return (
            PreQuantumInput(
                classical_reference=rhf,
                qubit_hamiltonian=qh,
                canonical_active_space_integral_pack=None,
                meta={"source": "projection_fragment_mulliken_mo"},
            ),
            None,
        )
    if not sol.capabilities.supports_restricted_active_space_qubit_hamiltonian:
        raise PipelineError(
            "This pipeline stage builds a qubit Hamiltonian from restricted active-space MO integrals; "
            f"the selected backend {sol.capabilities.backend_id!r} does not provide "
            "a canonical active-space integral pack yet."
        )
    pack = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        rhf,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
    )
    qh = molecular_hamiltonian_from_canonical_active_space_pack(
        pack,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
        fermion_qubit_mapping=cfg.active_space.fermion_qubit_mapping,
        prefer_restricted_spatial_fermion_for_jordan_wigner=cfg.active_space.prefer_restricted_spatial_fermion_for_jordan_wigner,
        jordan_wigner_coeff_atol=cfg.active_space.jordan_wigner_coeff_atol,
        classical_reference_for_meta=rhf,
    )
    return (
        PreQuantumInput(
            classical_reference=rhf,
            qubit_hamiltonian=qh,
            canonical_active_space_integral_pack=pack,
            meta={"source": "canonical_active_space_integral_pack"},
        ),
        None,
    )


def hamiltonian(cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference) -> QubitHamiltonian:
    pre_q, _ = hamiltonian_with_schmidt_context(cfg, rhf)
    return pre_q.qubit_hamiltonian

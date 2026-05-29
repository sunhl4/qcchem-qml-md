from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from qchem_stack.chem.energy_components import build_energy_components_v1
from qchem_stack.config import ExperimentConfig  # noqa: TC001 — runtime helper
from qchem_stack.config._experiment_validation import (
    EXPERIMENT_CROSS_VALIDATORS_WITH_CAPS,
)
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.stages import (
    PreQuantumStageArtifacts,
    ScfStageArtifacts,
    mark_stage_done,
)

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.chem.pre_quantum_input import PreQuantumInput
    from qchem_stack.chem.solvers.base import SolverCapabilities
    from qchem_stack.orchestration.run_context import PipelineStageTimer


def _require_cas_active_counts(cfg: ExperimentConfig) -> tuple[int, int]:
    n_orbitals = cfg.active_space.cas.n_orbitals
    n_electrons = cfg.active_space.cas.n_electrons
    if n_orbitals is None or n_electrons is None:
        raise PipelineError("CAS active space requires n_orbitals and n_electrons.")
    return int(n_orbitals), int(n_electrons)


@dataclass(frozen=True)
class ScfStageContext:
    is_precomputed_driver_fn: Callable[[ExperimentConfig], bool]
    solver_capabilities_fn: Callable[[ExperimentConfig], SolverCapabilities]
    run_scf_fn: Callable[[ExperimentConfig], ClassicalMeanFieldReference]
    refine_active_space_fn: Callable[
        [ExperimentConfig, ClassicalMeanFieldReference], ExperimentConfig
    ]
    embedding_input_payload_fn: Callable[
        [ExperimentConfig, ClassicalMeanFieldReference], dict[str, Any] | None
    ]


@dataclass(frozen=True)
class PreQuantumStageContext:
    is_precomputed_driver_fn: Callable[[ExperimentConfig], bool]
    precomputed_pre_quantum_input_fn: Callable[
        [ExperimentConfig, ClassicalMeanFieldReference, Path | None], PreQuantumInput
    ]
    hamiltonian_with_context_fn: Callable[
        [ExperimentConfig, ClassicalMeanFieldReference, Path | None],
        tuple[PreQuantumInput, dict[str, Any] | None],
    ]


def run_scf_stage(
    cfg: ExperimentConfig,
    *,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
    logger: logging.Logger,
    context: ScfStageContext,
) -> ScfStageArtifacts:
    precomputed_mode = context.is_precomputed_driver_fn(cfg)
    solver_caps = context.solver_capabilities_fn(cfg)
    for validator in EXPERIMENT_CROSS_VALIDATORS_WITH_CAPS:
        validator(cfg, caps=solver_caps)
    rhf = context.run_scf_fn(cfg)
    if not precomputed_mode:
        cfg = context.refine_active_space_fn(cfg, rhf)
    nuclear_au = rhf.nuclear_repulsion_au()
    solvent_eps = (
        float(cfg.chemistry_extended.solvent.epsilon)
        if cfg.chemistry_extended.solvent.model == "ddcosmo"
        else None
    )
    energy_components = build_energy_components_v1(
        nuclear_repulsion_au=nuclear_au,
        mean_field_total_au=float(rhf.e_tot),
        solvent_model=str(cfg.chemistry_extended.solvent.model),
        solvent_dielectric=solvent_eps,
        energy_accounting_model=str(
            rhf.driver_meta.get("energy_accounting_model", "mf_e_tot_direct")
        ),
    )
    from qchem_stack.chem.embedding.oniom import enrich_energy_components_oniom_if_configured

    energy_components = enrich_energy_components_oniom_if_configured(
        cfg, cfg.molecule.coordinates, energy_components
    )
    classical_benchmarks: dict[str, Any] | None = None
    rdm_bundle_meta: dict[str, Any] | None = None
    rdm_correction_report: dict[str, Any] | None = None
    rdm_correction_readiness: dict[str, Any] | None = None
    embedding_input_payload = context.embedding_input_payload_fn(cfg, rhf)
    if precomputed_mode and cfg.chemistry_extended.benchmarks.enabled:
        raise PipelineError(
            "classical_benchmark_enabled is unsupported with scf.driver='precomputed' "
            "(no runtime post-HF backend attached)."
        )
    if cfg.chemistry_extended.benchmarks.enabled:
        from qchem_stack.chem.classical_benchmarks import (
            ClassicalBenchmarkContext,
            run_classical_post_hf_benchmarks,
        )

        n_active_orbitals, n_active_electrons = _require_cas_active_counts(cfg)
        classical_benchmarks = run_classical_post_hf_benchmarks(
            cfg,
            ClassicalBenchmarkContext(
                mean_field_reference=rhf,
                reference_scf_method=str(cfg.scf.method),
                n_active_orbitals=n_active_orbitals,
                n_active_electrons=n_active_electrons,
            ),
        )
    if precomputed_mode and cfg.chemistry_extended.post_hf.rdm_correction_method != "none":
        raise PipelineError(
            "rdm_correction_method requires live backend hooks and is unsupported with "
            "scf.driver='precomputed'."
        )
    if cfg.chemistry_extended.post_hf.rdm_correction_method != "none":
        from qchem_stack.chem.kernels.dispatch import run_nevpt2_casci
        from qchem_stack.integrations.rdm_corrections import (
            build_rdm_correction_readiness,
            rdm_bundle_from_mean_field,
            run_rdm_correction,
        )

        if not solver_caps.supports_rdm_correction_hooks:
            raise PipelineError(
                "rdm_correction_method requires backend RDM extraction support "
                f"(backend={solver_caps.backend_id!r})."
            )
        rdmb = rdm_bundle_from_mean_field(rhf)
        rdm_bundle_meta = dict(rdmb.metadata)
        rdm_m = cfg.chemistry_extended.post_hf.rdm_correction_method
        if rdm_m in ("stub_nevpt2", "stub_ac0"):
            rdm_correction_report = cast("dict[str, Any]", run_rdm_correction(rdm_m, rdmb))
        elif rdm_m in ("pyscf_nevpt2_casci", "psi4_nevpt2_casci"):
            if not solver_caps.supports_rdm_nevpt2_casci:
                raise PipelineError(
                    f"rdm_correction_method={rdm_m!r} requires backend NEVPT2/CASCI support "
                    f"(backend={solver_caps.backend_id!r})."
                )
            n_active_orbitals, n_active_electrons = _require_cas_active_counts(cfg)
            rdm_correction_report = cast(
                "dict[str, Any]",
                run_nevpt2_casci(
                    cfg,
                    rhf,
                    n_active_orbitals,
                    n_active_electrons,
                ),
            )
            from qchem_stack.chem.integration.meta_schema import (
                merge_rdm_correction_bindings_into_reference,
            )

            merge_rdm_correction_bindings_into_reference(rhf.driver_meta, rdm_correction_report)
        else:
            raise ValueError(f"Unsupported rdm_correction_method: {rdm_m!r}")
        rdm_correction_readiness = cast(
            "dict[str, Any]",
            build_rdm_correction_readiness(
                requested_method=rdm_m,
                correction_report=rdm_correction_report,
                bundle_meta=rdm_bundle_meta or {},
            ),
        )
    mark_stage_done(
        profile=profile,
        emit=emit,
        logger=logger,
        stage="scf_done",
        experiment_id=str(cfg.experiment_id),
        extra_message=f"E_tot_au={float(rhf.e_tot):.10f}",
    )
    return ScfStageArtifacts(
        cfg=cfg,
        rhf=rhf,
        precomputed_mode=precomputed_mode,
        solver_caps=solver_caps,
        energy_components=energy_components,
        embedding_input_payload=embedding_input_payload,
        classical_benchmarks=classical_benchmarks,
        rdm_bundle_meta=rdm_bundle_meta,
        rdm_correction_report=rdm_correction_report,
        rdm_correction_readiness=rdm_correction_readiness,
    )


def build_pre_quantum_stage(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
    logger: logging.Logger,
    context: PreQuantumStageContext,
) -> PreQuantumStageArtifacts:
    if context.is_precomputed_driver_fn(cfg):
        pre_q_input = context.precomputed_pre_quantum_input_fn(cfg, rhf, cfg_path)
        schmidt_ctx = None
    else:
        pre_q_input, schmidt_ctx = context.hamiltonian_with_context_fn(cfg, rhf, cfg_path)
    qh: QubitHamiltonian = pre_q_input.qubit_hamiltonian
    mark_stage_done(
        profile=profile,
        emit=emit,
        logger=logger,
        stage="hamiltonian_built",
        experiment_id=str(cfg.experiment_id),
        extra_message=f"n_qubits={qh.n_qubits} integral_source={(qh.meta or {}).get('integral_source')}",
    )
    return PreQuantumStageArtifacts(
        pre_quantum_input=pre_q_input,
        schmidt_ctx=schmidt_ctx,
        qh=qh,
    )

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.energy_components import build_energy_components_v1
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.stages import (
    PreQuantumStageArtifacts,
    ScfStageArtifacts,
    mark_stage_done,
)


@dataclass(frozen=True)
class ScfStageContext:
    is_precomputed_driver_fn: Callable[[ExperimentConfig], bool]
    solver_capabilities_fn: Callable[[ExperimentConfig], Any]
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
    profile: Any,
    emit: Callable[[str], None],
    logger: logging.Logger,
    context: ScfStageContext,
) -> ScfStageArtifacts:
    precomputed_mode = context.is_precomputed_driver_fn(cfg)
    solver_caps = context.solver_capabilities_fn(cfg)
    rhf = context.run_scf_fn(cfg)
    if not precomputed_mode:
        cfg = context.refine_active_space_fn(cfg, rhf)
    nuclear_au = rhf.nuclear_repulsion_au()
    solvent_eps = (
        float(cfg.chemistry_extended.ddcosmo_epsilon)
        if cfg.chemistry_extended.solvent_model == "ddcosmo"
        else None
    )
    energy_components = build_energy_components_v1(
        nuclear_repulsion_au=nuclear_au,
        mean_field_total_au=float(rhf.e_tot),
        solvent_model=str(cfg.chemistry_extended.solvent_model),
        solvent_dielectric=solvent_eps,
        energy_accounting_model=str(
            rhf.driver_meta.get("energy_accounting_model", "mf_e_tot_direct")
        ),
    )
    classical_benchmarks: dict[str, Any] | None = None
    rdm_bundle_meta: dict[str, Any] | None = None
    rdm_correction_report: dict[str, Any] | None = None
    rdm_correction_readiness: dict[str, Any] | None = None
    embedding_input_payload = context.embedding_input_payload_fn(cfg, rhf)
    if precomputed_mode and cfg.chemistry_extended.classical_benchmark_enabled:
        raise PipelineError(
            "classical_benchmark_enabled is unsupported with scf.driver='precomputed' "
            "(no runtime post-HF backend attached)."
        )
    if cfg.chemistry_extended.classical_benchmark_enabled:
        from qchem_stack.chem.classical_benchmarks import (
            ClassicalBenchmarkContext,
            run_classical_post_hf_benchmarks,
        )

        classical_benchmarks = run_classical_post_hf_benchmarks(
            cfg,
            ClassicalBenchmarkContext(
                mean_field_reference=rhf,
                reference_scf_method=str(cfg.scf.method),
                n_active_orbitals=int(cfg.active_space.n_active_orbitals),
                n_active_electrons=int(cfg.active_space.n_active_electrons),
            ),
        )
    if precomputed_mode and cfg.chemistry_extended.rdm_correction_method != "none":
        raise PipelineError(
            "rdm_correction_method requires live backend hooks and is unsupported with "
            "scf.driver='precomputed'."
        )
    if cfg.chemistry_extended.rdm_correction_method != "none":
        from qchem_stack.integrations.rdm_corrections import (
            build_rdm_correction_readiness,
            rdm_bundle_from_mean_field,
            run_pyscf_nevpt2_casci_correction,
            run_rdm_correction,
        )

        if not solver_caps.supports_rdm_correction_hooks:
            raise PipelineError(
                "rdm_correction_method requires backend RDM extraction support "
                f"(backend={solver_caps.backend_id!r})."
            )
        rdmb = rdm_bundle_from_mean_field(rhf)
        rdm_bundle_meta = dict(rdmb.metadata)
        rdm_m = cfg.chemistry_extended.rdm_correction_method
        if rdm_m in ("stub_nevpt2", "stub_ac0"):
            rdm_correction_report = run_rdm_correction(rdm_m, rdmb)
        elif rdm_m == "pyscf_nevpt2_casci":
            if not solver_caps.supports_rdm_nevpt2_casci:
                raise PipelineError(
                    "rdm_correction_method='pyscf_nevpt2_casci' requires backend support "
                    f"(backend={solver_caps.backend_id!r})."
                )
            rdm_correction_report = run_pyscf_nevpt2_casci_correction(
                rhf,
                int(cfg.active_space.n_active_orbitals),
                int(cfg.active_space.n_active_electrons),
            )
        else:
            raise ValueError(f"Unsupported rdm_correction_method: {rdm_m!r}")
        rdm_correction_readiness = build_rdm_correction_readiness(
            requested_method=rdm_m,
            correction_report=rdm_correction_report,
            bundle_meta=rdm_bundle_meta,
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
    profile: Any,
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

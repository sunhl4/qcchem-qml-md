from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.backends.spec import summarize_circuit_shot_rows
from qchem_stack.chem.bridges.run_build_cache import RunBuildCache
from qchem_stack.chem.embedding.dmet import (
    DMETContext,
    QubitHamiltonianFragmentSolverExact,
    QubitHamiltonianFragmentSolverVQE,
)
from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
)
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input_with_context
from qchem_stack.chem.pre_quantum_builder_registry import list_pre_quantum_branch_builders
from qchem_stack.chem.integrals.exporter_registry import list_active_space_integral_exporters
from qchem_stack.config import (
    ExperimentConfig,
    backend_spec_from_config,
    compiler_pass_bundle_from_config,
    load_experiment_config,
)
from qchem_stack.integrations.dmet_self_consistent import OneShotEmbeddingDriver
from qchem_stack.jobs.nexus_analog import nexus_analog_ledger_from_rows
from qchem_stack.jobs.nexus_cloud import nexus_cloud_repro_sidecar
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.mitigation.pmsv import PMSVConfig
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.mitigation.qermit_runtime import execute_mitigation_dag_runtime
from qchem_stack.orchestration.parity_finalize import (
    finalize_open_stack_parity_snapshot as _finalize_open_stack_parity_snapshot_impl,
)
from qchem_stack.orchestration.parity_finalize import (
    schmidt_per_fragment_vqe_parity_summary as _schmidt_per_fragment_vqe_parity_summary_impl,
)
from qchem_stack.orchestration.embedding_workflow_stage import (
    apply_embedding_workflow_stage,
)
from qchem_stack.orchestration.excited_stages import (
    build_excited_resource_summary_for_export,
    excited_shot_channel_upper_bounds as _excited_shot_channel_upper_bounds,
    excited_shots_upper_bound as _excited_shots_upper_bound,
    run_excited_stages,
)
from qchem_stack.orchestration.protocol_finalize_stage import (
    resource_summary_excited_only as _resource_summary_excited_only,
)
from qchem_stack.orchestration.protocol_finalize_stage import (
    run_protocol_and_finalize_stage,
)
from qchem_stack.orchestration.protocol_finalize_stage import protocol_for_job

from qchem_stack.orchestration.precomputed_stage import (
    is_precomputed_driver,
    normalize_precomputed_bundle_path,
    precomputed_pre_quantum_input,
)
from qchem_stack.orchestration.repro_metadata import (
    collect_repro_metadata_impl as _collect_repro_metadata_impl,
)
from qchem_stack.orchestration.repro_snapshot import (
    append_open_stack_parity_fields as _append_open_stack_parity_fields_impl,
)
from qchem_stack.orchestration.repro_snapshot import (
    repro_quantum_snapshot as _repro_quantum_snapshot_impl,
)
from qchem_stack.orchestration.repro_summary import (
    attach_run_summary as _attach_run_summary_impl,
)
from qchem_stack.orchestration.repro_summary import (
    classical_benchmark_summary as _classical_benchmark_summary_impl,
)
from qchem_stack.orchestration.run_context import PipelineStageTimer, RunContext
from qchem_stack.orchestration.scf_stage import (
    embedding_input_system_payload,
    refine_mean_field_for_active_space,
    run_scf_reference,
    solver_capabilities,
)
from qchem_stack.orchestration.stage_execution import (
    PreQuantumStageContext,
    ScfStageContext,
    build_pre_quantum_stage,
    run_scf_stage,
)
from qchem_stack.protocols.protocol import PauliAveragingProtocol
from qchem_stack.quantum.algorithms.excited import QSE, VQD
from qchem_stack.quantum.variational_plugins.registry import run_variational_stage
from qchem_stack.quantum.variational_plugins.spec import VariationalRunContext

_pipeline_log = logging.getLogger(__name__)


def _repro_quantum_snapshot(cfg: ExperimentConfig, qh: QubitHamiltonian | None) -> dict[str, Any]:
    return _repro_quantum_snapshot_impl(cfg, qh)


def _append_open_stack_parity_fields(snap: dict[str, Any], cfg: ExperimentConfig) -> None:
    _append_open_stack_parity_fields_impl(snap, cfg)


def _schmidt_per_fragment_vqe_parity_summary(spfv: dict[str, Any]) -> dict[str, Any]:
    return _schmidt_per_fragment_vqe_parity_summary_impl(spfv)


def _finalize_open_stack_parity_snapshot(
    out: dict[str, Any],
    cfg: ExperimentConfig,
    proto: PauliAveragingProtocol | None,
) -> None:
    _finalize_open_stack_parity_snapshot_impl(out, cfg, proto)


def collect_repro_metadata(
    cfg: ExperimentConfig,
    cfg_path: Path | None = None,
    qh: QubitHamiltonian | None = None,
) -> dict[str, Any]:
    return _collect_repro_metadata_impl(
        cfg,
        parity_snapshot_fn=_repro_quantum_snapshot,
        cfg_path=cfg_path,
        qh=qh,
    )


def _classical_benchmark_summary(cb: dict[str, Any]) -> dict[str, Any]:
    return _classical_benchmark_summary_impl(cb)


def _attach_run_summary(out: dict[str, Any], cfg: ExperimentConfig) -> None:
    _attach_run_summary_impl(out, cfg)


# Backward-compatible aliases for tests and scripts.
_run_scf = run_scf_reference


def run_pipeline_sync(
    cfg: ExperimentConfig,
    *,
    cfg_path: Path | None = None,
    hamiltonian_out: list[QubitHamiltonian] | None = None,
    run_context: RunContext | None = None,
    job_timeline_emit: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Run chemistry + VQE/ADAPT + optional VQD/QSE/SCEOM + optional Pauli protocol in-process."""
    cfg = normalize_precomputed_bundle_path(cfg, cfg_path=cfg_path)
    q = cfg.quantum
    profile = PipelineStageTimer()
    build_cache = RunBuildCache()

    def _emit(stage: str) -> None:
        if job_timeline_emit is not None:
            job_timeline_emit(
                {"kind": "pipeline_stage", "stage": stage, "status": "RUNNING"},
            )

    scf_stage = run_scf_stage(
        cfg,
        profile=profile,
        emit=_emit,
        logger=_pipeline_log,
        context=ScfStageContext(
            is_precomputed_driver_fn=is_precomputed_driver,
            solver_capabilities_fn=solver_capabilities,
            run_scf_fn=run_scf_reference,
            refine_active_space_fn=refine_mean_field_for_active_space,
            embedding_input_payload_fn=embedding_input_system_payload,
        ),
    )
    cfg = scf_stage.cfg
    rhf = scf_stage.rhf
    pre_q_stage = build_pre_quantum_stage(
        cfg,
        rhf,
        cfg_path=cfg_path,
        profile=profile,
        emit=_emit,
        logger=_pipeline_log,
        context=PreQuantumStageContext(
            is_precomputed_driver_fn=is_precomputed_driver,
            precomputed_pre_quantum_input_fn=lambda c, r, p: precomputed_pre_quantum_input(
                c, r, cfg_path=p
            ),
            hamiltonian_with_context_fn=lambda c, r, p: build_pre_quantum_input_with_context(
                c, r, cfg_path=p, cache=build_cache, profile=profile
            ),
        ),
    )
    pre_q_input = pre_q_stage.pre_quantum_input
    schmidt_ctx = pre_q_stage.schmidt_ctx
    qh = pre_q_stage.qh
    energy_components = scf_stage.energy_components
    embedding_input_payload = scf_stage.embedding_input_payload
    classical_benchmarks = scf_stage.classical_benchmarks
    rdm_bundle_meta = scf_stage.rdm_bundle_meta
    rdm_correction_report = scf_stage.rdm_correction_report
    rdm_correction_readiness = scf_stage.rdm_correction_readiness
    if hamiltonian_out is not None:
        hamiltonian_out.clear()
        hamiltonian_out.append(qh)
    repro = collect_repro_metadata(cfg, cfg_path, qh)
    if run_context is not None:
        repro["run_context"] = run_context.to_repro_dict()
    bspec = backend_spec_from_config(cfg)
    exe = executor_from_spec(bspec)
    bundle = compiler_pass_bundle_from_config(cfg)

    vctx = VariationalRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=exe,
        seed=cfg.random_seed,
        pre_quantum_input=pre_q_input,
    )
    stage = run_variational_stage(vctx)
    algo_meta = stage.algo_meta_must_include_algorithm(cfg.quantum.algorithm)
    angles = stage.angles
    energy_pre = float(stage.energy)

    profile.mark("variational_done")
    _emit("variational_done")

    _pipeline_log.info(
        "pipeline variational_done experiment_id=%s algorithm=%s E_var_au=%.10f",
        cfg.experiment_id,
        q.algorithm,
        float(energy_pre),
    )

    out: dict[str, Any] = {
        "repro": repro,
        "scf_energy": float(rhf.e_tot),
        "energy_after_variational": float(energy_pre),
        "angles": angles.tolist() if isinstance(angles, np.ndarray) else list(angles),
        **algo_meta,
    }
    out["pre_quantum_input"] = pre_q_input.as_summary_dict()
    if classical_benchmarks is not None:
        out["classical_benchmarks"] = classical_benchmarks
        out["classical_benchmark_summary"] = _classical_benchmark_summary(classical_benchmarks)
    if embedding_input_payload is not None:
        out["embedding_input_system"] = embedding_input_payload
    out["energy_components"] = energy_components
    if rdm_bundle_meta is not None:
        out["rdm_bundle_meta"] = rdm_bundle_meta
    if rdm_correction_report is not None:
        out["rdm_correction"] = rdm_correction_report
    if rdm_correction_readiness is not None:
        out["rdm_correction_readiness"] = rdm_correction_readiness
    out["hamiltonian_meta"] = dict(qh.meta)
    out["pre_quantum_build_cache"] = build_cache.stats_dict()
    repro_ps = out.get("repro", {}).get("parity_snapshot")
    if isinstance(repro_ps, dict):
        repro_ps["pre_quantum_build_cache_v1"] = dict(out["pre_quantum_build_cache"])
        repro_ps["active_space_exporters_registry_v1"] = {
            "schema": "active_space_exporters_registry_v1",
            "backend_tags": list(list_active_space_integral_exporters()),
        }
        repro_ps["pre_quantum_branch_registry_v1"] = {
            "schema": "pre_quantum_branch_registry_v1",
            "path_ids": list(list_pre_quantum_branch_builders()),
        }
        pqi_sum = out.get("pre_quantum_input")
        if isinstance(pqi_sum, dict):
            repro_ps["pre_quantum_handoff_v1"] = {
                k: pqi_sum[k]
                for k in (
                    "source",
                    "backend_tag",
                    "hamiltonian_fingerprint",
                    "hamiltonian_branch",
                    "hamiltonian_fixed_before_variational",
                    "post_variational_embedding_audit_only",
                    "reference_energy_au",
                    "scf_energy_au",
                    "n_active_orbitals",
                    "n_active_electrons",
                )
                if k in pqi_sum and pqi_sum[k] is not None
            }
    apply_embedding_workflow_stage(
        cfg,
        out=out,
        qh=qh,
        exe=exe,
        embedding_input_payload=embedding_input_payload,
        schmidt_ctx=schmidt_ctx,
        rhf=rhf,
        cfg_path=cfg_path,
        profile=profile,
        emit=_emit,
    )
    excited_rs = run_excited_stages(
        cfg,
        qh=qh,
        exe=exe,
        angles=angles,
        energy_pre=float(energy_pre),
        out=out,
        profile=profile,
        emit=_emit,
    )

    return run_protocol_and_finalize_stage(
        cfg,
        out=out,
        qh=qh,
        angles=angles,
        excited_rs=excited_rs,
        bspec=bspec,
        exe=exe,
        bundle=bundle,
        rhf=rhf,
        cfg_path=cfg_path,
        profile=profile,
        emit=_emit,
    )


def run_pipeline_from_config(
    cfg_path: str | Path,
    *,
    job_db: Path | None = None,
    enqueue_only: bool = False,
    run_context: RunContext | None = None,
) -> dict[str, Any]:
    """Sync pipeline plus optional job enqueue (pickled :class:`PauliAveragingProtocol`)."""
    p = Path(cfg_path)
    cfg = load_experiment_config(p)
    qh_lane: list[QubitHamiltonian] = []
    sync = run_pipeline_sync(cfg, cfg_path=p, hamiltonian_out=qh_lane, run_context=run_context)

    if job_db is None or not cfg.quantum.use_pauli_protocol:
        return sync

    qh = qh_lane[0]
    angles = np.asarray(sync["angles"], dtype=float)
    bspec2 = backend_spec_from_config(cfg)
    exe2 = executor_from_spec(bspec2)
    bundle2 = compiler_pass_bundle_from_config(cfg)
    proto = protocol_for_job(cfg, qh, bspec=bspec2, exe=exe2, bundle=bundle2)
    proto.build(angles, hea_depth=cfg.quantum.vqe_depth)
    proto.compile()
    blob = proto.dumps()
    ph = hashlib.sha256(blob).hexdigest()[:24]
    store = SqliteJobStore(job_db)
    handle = proto.launch(store)
    sync["job"] = {"job_id": handle.job_id, "protocol_hash": ph, "store": str(job_db)}
    if not enqueue_only:
        PauliAveragingProtocol.process_job(store, handle.job_id)
        sync["job_result"] = store.result(handle.job_id)
    _attach_run_summary(sync, cfg)
    return sync



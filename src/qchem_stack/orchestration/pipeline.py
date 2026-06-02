"""In-process pipeline: SCF → pre-quantum → variational → excited → protocol finalize.

Orchestration wires chem, quantum, and backends; it must not be imported from those layers.

Stage map (``run_pipeline_sync``)
------------------------------------
1. **scf** — ``run_scf_stage``: reference MF, active-space refinement, embedding payload,
   classical benchmarks, optional RDM bundle metadata.
2. **pre_quantum** — ``build_pre_quantum_stage``: Schmidt / integral handoff → ``QubitHamiltonian``.
3. **repro** — ``collect_repro_metadata`` after Hamiltonian is fixed for variational use.
4. **variational** — ``run_variational_stage`` (VQE / ADAPT / registry plugins).
5. **embedding_workflow** — ``apply_embedding_workflow_stage`` (DMET / fragment VQE when configured).
6. **excited** — ``run_excited_stages`` (VQD / QSE / SCEOM per config).
7. **protocol_finalize** — ``run_protocol_and_finalize_stage``: optional Pauli averaging,
   mitigation DAG, resource summaries, ``attach_run_summary``.

``run_pipeline_from_config`` adds an optional **job_enqueue** step when
``pauli_protocol_enabled(cfg)`` and ``job_db`` are set (build → compile → SQLite store).
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import numpy as np

from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.chem.bridges.run_build_cache import RunBuildCache
from qchem_stack.chem.integrals.exporter_registry import list_active_space_integral_exporters
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input_with_context
from qchem_stack.chem.pre_quantum_builder_registry import list_pre_quantum_branch_builders
from qchem_stack.config import (
    ExperimentConfig,
    backend_spec_from_config,
    compiler_pass_bundle_from_config,
    load_experiment_config,
)
from qchem_stack.config.quantum_helpers import (
    pauli_protocol_enabled,
    resolve_variational_algorithm,
    resolve_vqe_depth,
)
from qchem_stack.contracts.schema_ids import (
    ACTIVE_SPACE_EXPORTERS_REGISTRY_V1,
    PRE_QUANTUM_BRANCH_REGISTRY_V1,
)
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.orchestration.embedding_workflow_stage import (
    apply_embedding_workflow_stage,
)
from qchem_stack.orchestration.excited_stages import (
    run_excited_stages,
)
from qchem_stack.orchestration.pipeline_event_hooks import (
    emit_stage_event,
    trace_id_from_run_context,
)
from qchem_stack.orchestration.pipeline_events import PipelineEvents
from qchem_stack.orchestration.pipeline_result import PipelineResultV1, tag_pipeline_result
from qchem_stack.orchestration.precomputed_stage import (
    is_precomputed_driver,
    normalize_precomputed_bundle_path,
    precomputed_pre_quantum_input,
)
from qchem_stack.orchestration.protocol_finalize_stage import (
    ansatz_prep_for_job,
    protocol_for_job,
    run_protocol_and_finalize_stage,
)
from qchem_stack.orchestration.repro_metadata import (
    collect_repro_metadata_impl as _collect_repro_metadata_impl,
)
from qchem_stack.orchestration.repro_snapshot import repro_quantum_snapshot
from qchem_stack.orchestration.repro_summary import (
    attach_run_summary,
    classical_benchmark_summary,
)
from qchem_stack.orchestration.run_context import (
    PipelineStageTimer,
    RunContext,
    emit_pipeline_stage_json_log,
)
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
from qchem_stack.quantum.variational_plugins.registry import run_variational_stage
from qchem_stack.quantum.variational_plugins.spec import VariationalRunContext

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.hamiltonian import QubitHamiltonian

_pipeline_log = logging.getLogger(__name__)


def collect_repro_metadata(
    cfg: ExperimentConfig,
    cfg_path: Path | None = None,
    qh: QubitHamiltonian | None = None,
) -> dict[str, Any]:
    return _collect_repro_metadata_impl(
        cfg,
        parity_snapshot_fn=repro_quantum_snapshot,
        cfg_path=cfg_path,
        qh=qh,
    )


def _assemble_pipeline_result_dict(
    *,
    repro: dict[str, Any],
    rhf: Any,
    energy_pre: float,
    angles: Any,
    algo_meta: dict[str, Any],
    algorithm_report: Any,
    pre_q_input: Any,
    classical_benchmarks: dict[str, Any] | None,
    embedding_input_payload: Any,
    energy_components: Any,
    rdm_bundle_meta: dict[str, Any] | None,
    rdm_correction_report: Any,
    rdm_correction_readiness: Any,
    qh: QubitHamiltonian,
    build_cache: RunBuildCache,
) -> dict[str, Any]:
    """Assemble the post-variational result dict (pre embedding/excited/protocol stages)."""
    out: dict[str, Any] = {
        "repro": repro,
        "scf_energy": float(rhf.e_tot),
        "energy_after_variational": float(energy_pre),
        "angles": angles.tolist() if isinstance(angles, np.ndarray) else list(angles),
        **algo_meta,
    }
    if algorithm_report is not None:
        out["algorithm_report"] = algorithm_report
    out["pre_quantum_input"] = pre_q_input.as_summary_dict()
    if classical_benchmarks is not None:
        out["classical_benchmarks"] = classical_benchmarks
        out["classical_benchmark_summary"] = classical_benchmark_summary(classical_benchmarks)
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
    return out


def _patch_repro_parity_snapshot(out: dict[str, Any]) -> None:
    """Augment ``repro.parity_snapshot`` with build-cache and registry exports in place."""
    repro_ps = out.get("repro", {}).get("parity_snapshot")
    if not isinstance(repro_ps, dict):
        return
    repro_ps["pre_quantum_build_cache_v1"] = dict(out["pre_quantum_build_cache"])
    repro_ps["active_space_exporters_registry_v1"] = {
        "schema": ACTIVE_SPACE_EXPORTERS_REGISTRY_V1,
        "backend_tags": list(list_active_space_integral_exporters()),
    }
    repro_ps["pre_quantum_branch_registry_v1"] = {
        "schema": PRE_QUANTUM_BRANCH_REGISTRY_V1,
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


def run_pipeline_sync(
    cfg: ExperimentConfig,
    *,
    cfg_path: Path | None = None,
    hamiltonian_out: list[QubitHamiltonian] | None = None,
    run_context: RunContext | None = None,
    job_timeline_emit: Callable[[dict[str, Any]], None] | None = None,
) -> PipelineResultV1:
    """Run chemistry + VQE/ADAPT + optional VQD/QSE/SCEOM + optional Pauli protocol in-process."""
    cfg = normalize_precomputed_bundle_path(cfg, cfg_path=cfg_path)
    q = cfg.quantum
    profile = PipelineStageTimer()
    build_cache = RunBuildCache()
    trace_id = trace_id_from_run_context(run_context)

    emit_stage_event(
        PipelineEvents.PIPELINE_STARTED,
        stage="pipeline",
        trace_id=trace_id,
        data={"experiment_id": cfg.experiment_id},
    )

    def _emit(stage: str) -> None:
        emit_pipeline_stage_json_log(
            stage,
            trace_id=run_context.trace_id if run_context is not None else None,
        )
        if job_timeline_emit is not None:
            job_timeline_emit(
                {"kind": "pipeline_stage", "stage": stage, "status": "RUNNING"},
            )

    emit_stage_event(PipelineEvents.SCF_STARTED, stage="scf", trace_id=trace_id)
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
    emit_stage_event(
        PipelineEvents.SCF_COMPLETED,
        stage="scf",
        trace_id=trace_id,
        data={"scf_energy": float(rhf.e_tot)},
    )
    emit_stage_event(PipelineEvents.PRE_QUANTUM_STARTED, stage="pre_quantum", trace_id=trace_id)
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
    emit_stage_event(
        PipelineEvents.PRE_QUANTUM_COMPLETED,
        stage="pre_quantum",
        trace_id=trace_id,
        data={"n_qubits": int(qh.n_qubits)},
    )
    repro = collect_repro_metadata(cfg, cfg_path, qh)
    if run_context is not None:
        repro["run_context"] = run_context.to_repro_dict()
    bspec = backend_spec_from_config(cfg)
    exe = executor_from_spec(bspec)
    bundle = compiler_pass_bundle_from_config(cfg)

    emit_stage_event(PipelineEvents.VARIATIONAL_STARTED, stage="variational", trace_id=trace_id)
    vctx = VariationalRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=exe,
        seed=cfg.random_seed,
        pre_quantum_input=pre_q_input,
    )
    stage = run_variational_stage(vctx)
    algo_meta = stage.algo_meta_must_include_algorithm(resolve_variational_algorithm(cfg))
    angles = stage.angles
    energy_pre = float(stage.energy)

    profile.mark("variational_done")
    _emit("variational_done")
    emit_stage_event(
        PipelineEvents.VARIATIONAL_COMPLETED,
        stage="variational",
        trace_id=trace_id,
        data={"energy_au": float(energy_pre), "algorithm": str(q.algorithm)},
    )

    _pipeline_log.info(
        "pipeline variational_done experiment_id=%s algorithm=%s E_var_au=%.10f",
        cfg.experiment_id,
        q.algorithm,
        float(energy_pre),
    )

    out = _assemble_pipeline_result_dict(
        repro=repro,
        rhf=rhf,
        energy_pre=energy_pre,
        angles=angles,
        algo_meta=algo_meta,
        algorithm_report=stage.algorithm_report,
        pre_q_input=pre_q_input,
        classical_benchmarks=classical_benchmarks,
        embedding_input_payload=embedding_input_payload,
        energy_components=energy_components,
        rdm_bundle_meta=rdm_bundle_meta,
        rdm_correction_report=rdm_correction_report,
        rdm_correction_readiness=rdm_correction_readiness,
        qh=qh,
        build_cache=build_cache,
    )
    _patch_repro_parity_snapshot(out)
    emit_stage_event(
        PipelineEvents.EMBEDDING_WORKFLOW_STARTED,
        stage="embedding_workflow",
        trace_id=trace_id,
    )
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
    emit_stage_event(
        PipelineEvents.EMBEDDING_WORKFLOW_COMPLETED,
        stage="embedding_workflow",
        trace_id=trace_id,
    )
    emit_stage_event(PipelineEvents.EXCITED_STARTED, stage="excited", trace_id=trace_id)
    excited_rs = run_excited_stages(
        cfg,
        qh=qh,
        exe=exe,
        angles=angles,
        energy_pre=float(energy_pre),
        out=out,
        profile=profile,
        emit=_emit,
        pre_quantum_input=pre_q_input,
    )
    emit_stage_event(PipelineEvents.EXCITED_COMPLETED, stage="excited", trace_id=trace_id)

    emit_stage_event(
        PipelineEvents.PROTOCOL_FINALIZE_STARTED,
        stage="protocol_finalize",
        trace_id=trace_id,
    )
    result = tag_pipeline_result(
        run_protocol_and_finalize_stage(
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
    )
    emit_stage_event(
        PipelineEvents.PROTOCOL_FINALIZE_COMPLETED,
        stage="protocol_finalize",
        trace_id=trace_id,
    )
    emit_stage_event(
        PipelineEvents.PIPELINE_COMPLETED,
        stage="pipeline",
        trace_id=trace_id,
        data={"experiment_id": cfg.experiment_id},
    )
    return result


def run_pipeline_from_config(
    cfg_path: str | Path,
    *,
    job_db: Path | None = None,
    enqueue_only: bool = False,
    run_context: RunContext | None = None,
) -> PipelineResultV1:
    """Sync pipeline plus optional job enqueue (pickled :class:`PauliAveragingProtocol`)."""
    p = Path(cfg_path)
    cfg = load_experiment_config(p)
    qh_lane: list[QubitHamiltonian] = []
    sync = run_pipeline_sync(cfg, cfg_path=p, hamiltonian_out=qh_lane, run_context=run_context)

    if job_db is None or not pauli_protocol_enabled(cfg):
        return tag_pipeline_result(sync)

    qh = qh_lane[0]
    angles_raw = sync.get("angles")
    if angles_raw is None:
        raise KeyError("pipeline sync missing angles before job enqueue")
    angles = np.asarray(angles_raw, dtype=float)
    bspec2 = backend_spec_from_config(cfg)
    exe2 = executor_from_spec(bspec2)
    bundle2 = compiler_pass_bundle_from_config(cfg)
    proto = protocol_for_job(cfg, qh, bspec=bspec2, exe=exe2, bundle=bundle2)
    prep = ansatz_prep_for_job(cfg, qh, angles, hea_depth=resolve_vqe_depth(cfg))
    from qchem_stack.protocols.product_contract import validate_pauli_protocol_for_config

    validate_pauli_protocol_for_config(cfg, ansatz=prep.kind)
    proto.build(angles, hea_depth=resolve_vqe_depth(cfg), ansatz_prep=prep)
    proto.compile()
    blob = proto.dumps()
    ph = hashlib.sha256(blob).hexdigest()[:24]
    store = SqliteJobStore(job_db)
    handle = proto.launch(store)
    sync["job"] = {"job_id": handle.job_id, "protocol_hash": ph, "store": str(job_db)}
    if not enqueue_only:
        PauliAveragingProtocol.process_job(store, handle.job_id)
        sync["job_result"] = store.result(handle.job_id)
    attach_run_summary(cast("dict[str, Any]", sync), cfg)
    return tag_pipeline_result(sync)


async def run_pipeline_async(
    cfg_path: str | Path,
    *,
    job_db: Path | None = None,
    enqueue_only: bool = False,
    run_context: RunContext | None = None,
    executor: ThreadPoolExecutor | None = None,
) -> PipelineResultV1:
    """Async wrapper for :func:`run_pipeline_from_config`.

    This runs the synchronous pipeline in a thread pool executor, allowing
    concurrent execution without blocking the event loop. Useful for:
    - FastAPI async endpoints
    - Batch processing multiple configurations
    - Integration with async job queues

    Parameters
    ----------
    cfg_path
        Path to the YAML configuration file.
    job_db
        Optional path to SQLite database for job persistence.
    enqueue_only
        If True, enqueue the job but don't execute it immediately.
    run_context
        Optional run context for distributed execution.
    executor
        Optional thread pool executor. If None, uses the default executor.

    Returns
    -------
    PipelineResultV1
        Pipeline execution results.

    Examples
    --------
    >>> import asyncio
    >>> result = asyncio.run(run_pipeline_async("configs/example_h2.yaml"))
    >>> print(result["energy_after_variational"])

    Notes
    -----
    This is a simple async wrapper. For true async-native execution (with
    async backends and job stores), see the roadmap in the documentation.
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        lambda: run_pipeline_from_config(
            cfg_path,
            job_db=job_db,
            enqueue_only=enqueue_only,
            run_context=run_context,
        ),
    )


async def run_pipeline_batch_async(
    cfg_paths: list[str | Path],
    *,
    job_db: Path | None = None,
    max_workers: int | None = None,
) -> list[PipelineResultV1]:
    """Run multiple pipelines concurrently in async mode.

    Parameters
    ----------
    cfg_paths
        List of configuration file paths to process.
    job_db
        Optional shared SQLite database for all jobs.
    max_workers
        Maximum number of concurrent pipelines. If None, uses CPU count.

    Returns
    -------
    list[PipelineResultV1]
        List of results in the same order as cfg_paths.

    Examples
    --------
    >>> import asyncio
    >>> configs = ["configs/example_h2.yaml", "configs/example_lih.yaml"]
    >>> results = asyncio.run(run_pipeline_batch_async(configs, max_workers=2))
    >>> for r in results:
    ...     print(r["energy_after_variational"])

    Notes
    -----
    Each pipeline runs in its own thread. Be mindful of memory usage when
    processing large batches of configurations.
    """
    executor = ThreadPoolExecutor(max_workers=max_workers)
    try:
        tasks = [
            run_pipeline_async(cfg_path, job_db=job_db, executor=executor) for cfg_path in cfg_paths
        ]
        return await asyncio.gather(*tasks)
    finally:
        executor.shutdown(wait=True)

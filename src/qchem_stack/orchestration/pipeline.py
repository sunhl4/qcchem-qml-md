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

import hashlib
import logging
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
from qchem_stack.orchestration import repro_snapshot
from qchem_stack.orchestration.embedding_workflow_stage import (
    apply_embedding_workflow_stage,
)
from qchem_stack.orchestration.excited_stages import (
    run_excited_stages,
)
from qchem_stack.orchestration.pipeline_result import PipelineResultV1, tag_pipeline_result
from qchem_stack.orchestration.precomputed_stage import (
    is_precomputed_driver,
    normalize_precomputed_bundle_path,
    precomputed_pre_quantum_input,
)
from qchem_stack.orchestration.protocol_finalize_stage import (
    protocol_for_job,
    run_protocol_and_finalize_stage,
)
from qchem_stack.orchestration.repro_metadata import (
    collect_repro_metadata_impl as _collect_repro_metadata_impl,
)
from qchem_stack.orchestration.repro_summary import (
    attach_run_summary,
    classical_benchmark_summary,
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
from qchem_stack.quantum.variational_plugins.registry import run_variational_stage
from qchem_stack.quantum.variational_plugins.spec import VariationalRunContext

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.hamiltonian import (
        QubitHamiltonian,
    )

_pipeline_log = logging.getLogger(__name__)


def collect_repro_metadata(
    cfg: ExperimentConfig,
    cfg_path: Path | None = None,
    qh: QubitHamiltonian | None = None,
) -> dict[str, Any]:
    return _collect_repro_metadata_impl(
        cfg,
        parity_snapshot_fn=repro_snapshot.repro_quantum_snapshot,
        cfg_path=cfg_path,
        qh=qh,
    )


# Backward-compatible aliases for tests and scripts.
_run_scf = run_scf_reference
_attach_run_summary = attach_run_summary


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
    algo_meta = stage.algo_meta_must_include_algorithm(resolve_variational_algorithm(cfg))
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
    if stage.algorithm_report is not None:
        out["algorithm_report"] = stage.algorithm_report
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
    repro_ps = out.get("repro", {}).get("parity_snapshot")
    if isinstance(repro_ps, dict):
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
        pre_quantum_input=pre_q_input,
    )

    return tag_pipeline_result(
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
    proto.build(angles, hea_depth=resolve_vqe_depth(cfg))
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

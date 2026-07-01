"""Registry stage runners for :func:`~qchem_stack.orchestration.pipeline_sync_runner.run_pipeline_sync`."""

from __future__ import annotations

import logging

from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input_with_context
from qchem_stack.config import backend_spec_from_config, compiler_pass_bundle_from_config
from qchem_stack.config.quantum_helpers import resolve_variational_algorithm
from qchem_stack.orchestration.embedding_workflow_stage import apply_embedding_workflow_stage
from qchem_stack.orchestration.excited_stages import run_excited_stages
from qchem_stack.orchestration.pipeline_assembly import (
    assemble_pipeline_result_dict,
    patch_repro_parity_snapshot,
)
from qchem_stack.orchestration.pipeline_result import tag_pipeline_result
from qchem_stack.orchestration.pipeline_sync_context import PipelineSyncContext
from qchem_stack.orchestration.precomputed_stage import (
    is_precomputed_driver,
    precomputed_pre_quantum_input,
)
from qchem_stack.orchestration.protocol_finalize_stage import run_protocol_and_finalize_stage
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
from qchem_stack.quantum.variational_plugins.registry import run_variational_stage
from qchem_stack.quantum.variational_plugins.spec import VariationalRunContext

_pipeline_log = logging.getLogger(__name__)


def _stage_emit(ctx: PipelineSyncContext, stage: str) -> None:
    from qchem_stack.orchestration.run_context import emit_pipeline_stage_json_log

    emit_pipeline_stage_json_log(
        stage,
        trace_id=ctx.run_context.trace_id if ctx.run_context is not None else None,
    )
    if ctx.job_timeline_emit is not None:
        ctx.job_timeline_emit(
            {"kind": "pipeline_stage", "stage": stage, "status": "RUNNING"},
        )


def run_scf_stage_ctx(ctx: PipelineSyncContext) -> None:
    ctx.stage_completion_data = {}
    scf_stage = run_scf_stage(
        ctx.cfg,
        profile=ctx.profile,
        emit=lambda s: _stage_emit(ctx, s),
        logger=_pipeline_log,
        context=ScfStageContext(
            is_precomputed_driver_fn=is_precomputed_driver,
            solver_capabilities_fn=solver_capabilities,
            run_scf_fn=run_scf_reference,
            refine_active_space_fn=refine_mean_field_for_active_space,
            embedding_input_payload_fn=embedding_input_system_payload,
        ),
    )
    ctx.cfg = scf_stage.cfg
    ctx.rhf = scf_stage.rhf
    ctx.energy_components = scf_stage.energy_components
    ctx.embedding_input_payload = scf_stage.embedding_input_payload
    ctx.classical_benchmarks = scf_stage.classical_benchmarks
    ctx.rdm_bundle_meta = scf_stage.rdm_bundle_meta
    ctx.rdm_correction_report = scf_stage.rdm_correction_report
    ctx.rdm_correction_readiness = scf_stage.rdm_correction_readiness
    ctx.stage_completion_data = {"scf_energy": float(scf_stage.rhf.e_tot)}


def run_pre_quantum_stage_ctx(ctx: PipelineSyncContext) -> None:
    ctx.stage_completion_data = {}
    assert ctx.rhf is not None
    pre_q_stage = build_pre_quantum_stage(
        ctx.cfg,
        ctx.rhf,
        cfg_path=ctx.cfg_path,
        profile=ctx.profile,
        emit=lambda s: _stage_emit(ctx, s),
        logger=_pipeline_log,
        context=PreQuantumStageContext(
            is_precomputed_driver_fn=is_precomputed_driver,
            precomputed_pre_quantum_input_fn=lambda c, r, p: precomputed_pre_quantum_input(
                c, r, cfg_path=p
            ),
            hamiltonian_with_context_fn=lambda c, r, p: build_pre_quantum_input_with_context(
                c, r, cfg_path=p, cache=ctx.build_cache, profile=ctx.profile
            ),
        ),
    )
    ctx.pre_q_input = pre_q_stage.pre_quantum_input
    ctx.schmidt_ctx = pre_q_stage.schmidt_ctx
    ctx.qh = pre_q_stage.qh
    if ctx.hamiltonian_out is not None:
        ctx.hamiltonian_out.clear()
        ctx.hamiltonian_out.append(pre_q_stage.qh)
    ctx.stage_completion_data = {"n_qubits": int(pre_q_stage.qh.n_qubits)}


def bind_post_pre_quantum_ctx(ctx: PipelineSyncContext) -> None:
    """Collect repro metadata and backend handles after Hamiltonian is fixed."""
    assert ctx.qh is not None
    ctx.repro = ctx.collect_repro_metadata_fn(ctx.cfg, ctx.cfg_path, ctx.qh)
    if ctx.run_context is not None:
        ctx.repro["run_context"] = ctx.run_context.to_repro_dict()
    ctx.bspec = backend_spec_from_config(ctx.cfg)
    ctx.exe = executor_from_spec(ctx.bspec)
    ctx.bundle = compiler_pass_bundle_from_config(ctx.cfg)


def run_variational_stage_ctx(ctx: PipelineSyncContext) -> None:
    ctx.stage_completion_data = {}
    assert ctx.qh is not None
    assert ctx.exe is not None
    assert ctx.pre_q_input is not None
    assert ctx.rhf is not None
    q = ctx.cfg.quantum
    vctx = VariationalRunContext(
        cfg=ctx.cfg,
        hamiltonian=ctx.qh,
        executor=ctx.exe,
        seed=ctx.cfg.random_seed,
        pre_quantum_input=ctx.pre_q_input,
    )
    stage = run_variational_stage(vctx)
    algo_meta = stage.algo_meta_must_include_algorithm(resolve_variational_algorithm(ctx.cfg))
    ctx.angles = stage.angles
    ctx.energy_pre = float(stage.energy)
    ctx.profile.mark("variational_done")
    _stage_emit(ctx, "variational_done")
    _pipeline_log.info(
        "pipeline variational_done experiment_id=%s algorithm=%s E_var_au=%.10f",
        ctx.cfg.experiment_id,
        q.algorithm,
        float(ctx.energy_pre),
    )
    ctx.out = assemble_pipeline_result_dict(
        repro=ctx.repro,
        rhf=ctx.rhf,
        energy_pre=ctx.energy_pre,
        angles=ctx.angles,
        algo_meta=algo_meta,
        algorithm_report=stage.algorithm_report,
        pre_q_input=ctx.pre_q_input,
        classical_benchmarks=ctx.classical_benchmarks,
        embedding_input_payload=ctx.embedding_input_payload,
        energy_components=ctx.energy_components,
        rdm_bundle_meta=ctx.rdm_bundle_meta,
        rdm_correction_report=ctx.rdm_correction_report,
        rdm_correction_readiness=ctx.rdm_correction_readiness,
        qh=ctx.qh,
        build_cache=ctx.build_cache,
    )
    patch_repro_parity_snapshot(ctx.out)
    ctx.stage_completion_data = {
        "energy_au": float(ctx.energy_pre),
        "algorithm": str(q.algorithm),
    }


def run_embedding_workflow_stage_ctx(ctx: PipelineSyncContext) -> None:
    ctx.stage_completion_data = {}
    assert ctx.qh is not None
    assert ctx.exe is not None
    assert ctx.rhf is not None
    apply_embedding_workflow_stage(
        ctx.cfg,
        out=ctx.out,
        qh=ctx.qh,
        exe=ctx.exe,
        embedding_input_payload=ctx.embedding_input_payload,
        schmidt_ctx=ctx.schmidt_ctx,
        rhf=ctx.rhf,
        cfg_path=ctx.cfg_path,
        profile=ctx.profile,
        emit=lambda s: _stage_emit(ctx, s),
    )


def run_excited_stage_ctx(ctx: PipelineSyncContext) -> None:
    ctx.stage_completion_data = {}
    assert ctx.qh is not None
    assert ctx.exe is not None
    assert ctx.angles is not None
    ctx.excited_rs = run_excited_stages(
        ctx.cfg,
        qh=ctx.qh,
        exe=ctx.exe,
        angles=ctx.angles,
        energy_pre=float(ctx.energy_pre),
        out=ctx.out,
        profile=ctx.profile,
        emit=lambda s: _stage_emit(ctx, s),
        pre_quantum_input=ctx.pre_q_input,
    )


def run_protocol_finalize_stage_ctx(ctx: PipelineSyncContext) -> None:
    ctx.stage_completion_data = {}
    assert ctx.qh is not None
    assert ctx.angles is not None
    assert ctx.bspec is not None
    assert ctx.exe is not None
    assert ctx.bundle is not None
    assert ctx.rhf is not None
    ctx.result = tag_pipeline_result(
        run_protocol_and_finalize_stage(
            ctx.cfg,
            out=ctx.out,
            qh=ctx.qh,
            angles=ctx.angles,
            excited_rs=ctx.excited_rs,
            bspec=ctx.bspec,
            exe=ctx.exe,
            bundle=ctx.bundle,
            rhf=ctx.rhf,
            cfg_path=ctx.cfg_path,
            profile=ctx.profile,
            emit=lambda s: _stage_emit(ctx, s),
        )
    )

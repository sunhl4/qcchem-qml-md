"""In-process sync pipeline body (registry-driven stages)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from qchem_stack.chem.bridges.run_build_cache import RunBuildCache
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.pipeline_event_hooks import (
    emit_stage_event,
    trace_id_from_run_context,
)
from qchem_stack.orchestration.pipeline_events import PipelineEvents
from qchem_stack.orchestration.pipeline_result import PipelineResultV1
from qchem_stack.orchestration.pipeline_sync_context import PipelineSyncContext
from qchem_stack.orchestration.precomputed_stage import normalize_precomputed_bundle_path
from qchem_stack.orchestration.run_context import PipelineStageTimer, RunContext
from qchem_stack.orchestration.stage_registry import (
    PIPELINE_STAGE_SPECS,
    PIPELINE_WRAPPER_LIFECYCLE,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from qchem_stack.chem.hamiltonian import QubitHamiltonian

_pipeline_log = logging.getLogger(__name__)


def _record_stage_failure_in_repro(ctx: PipelineSyncContext, *, stage: str, exc: Exception) -> None:
    if not isinstance(ctx.repro, dict):
        return
    rs = ctx.repro.setdefault("run_summary", {})
    if isinstance(rs, dict):
        rs["stage_failed"] = stage
        rs["error_type"] = type(exc).__name__
        rs["error_message"] = str(exc)


def _run_pipeline_stages(ctx: PipelineSyncContext) -> None:
    """Execute ordered stage specs with lifecycle events."""
    for spec in PIPELINE_STAGE_SPECS:
        lc = spec.lifecycle
        emit_stage_event(lc.started, stage=lc.name, trace_id=ctx.trace_id)
        try:
            spec.run(ctx)
            if spec.post_run is not None:
                spec.post_run(ctx)
        except Exception as exc:
            fail_data: dict[str, object] = {
                "error": str(exc),
                "error_type": type(exc).__name__,
            }
            emit_stage_event(
                lc.failed,
                stage=lc.name,
                trace_id=ctx.trace_id,
                data=fail_data,
            )
            emit_stage_event(
                PipelineEvents.PIPELINE_FAILED,
                stage=lc.name,
                trace_id=ctx.trace_id,
                data=fail_data,
            )
            _record_stage_failure_in_repro(ctx, stage=lc.name, exc=exc)
            raise PipelineError(f"stage {lc.name} failed: {exc}") from exc
        data = dict(ctx.stage_completion_data) if ctx.stage_completion_data else None
        emit_stage_event(
            lc.completed,
            stage=lc.name,
            trace_id=ctx.trace_id,
            data=data,
        )


def run_pipeline_sync(
    cfg: ExperimentConfig,
    *,
    cfg_path: Path | None = None,
    hamiltonian_out: list[QubitHamiltonian] | None = None,
    run_context: RunContext | None = None,
    job_timeline_emit: Callable[[dict[str, object]], None] | None = None,
    collect_repro_metadata_fn: Callable[..., dict[str, object]],
) -> PipelineResultV1:
    """Run chemistry + VQE/ADAPT + optional VQD/QSE/SCEOM + optional Pauli protocol in-process."""
    cfg = normalize_precomputed_bundle_path(cfg, cfg_path=cfg_path)
    trace_id = trace_id_from_run_context(run_context)
    ctx = PipelineSyncContext(
        cfg=cfg,
        cfg_path=cfg_path,
        profile=PipelineStageTimer(),
        build_cache=RunBuildCache(),
        trace_id=trace_id,
        run_context=run_context,
        hamiltonian_out=hamiltonian_out,
        job_timeline_emit=job_timeline_emit,
        collect_repro_metadata_fn=collect_repro_metadata_fn,
    )

    emit_stage_event(
        PIPELINE_WRAPPER_LIFECYCLE.started,
        stage=PIPELINE_WRAPPER_LIFECYCLE.name,
        trace_id=trace_id,
        data={"experiment_id": cfg.experiment_id},
    )
    _run_pipeline_stages(ctx)
    emit_stage_event(
        PIPELINE_WRAPPER_LIFECYCLE.completed,
        stage=PIPELINE_WRAPPER_LIFECYCLE.name,
        trace_id=trace_id,
        data={"experiment_id": cfg.experiment_id},
    )
    if ctx.result is None:
        raise PipelineError("pipeline finished without protocol_finalize result")
    return ctx.result

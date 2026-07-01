"""Thin helpers to emit :class:`PipelineEvent` from orchestration stages."""

from __future__ import annotations

import logging
import os

from qchem_stack.orchestration.pipeline_events import (
    emit_pipeline_event,
)

_log = logging.getLogger(__name__)


def _debug_events_enabled() -> bool:
    return os.environ.get("QCHEM_PIPELINE_DEBUG_EVENTS", "").lower() in {"1", "true", "yes"}


def emit_stage_event(
    event_name: str,
    *,
    stage: str | None = None,
    trace_id: str | None = None,
    data: dict[str, object] | None = None,
) -> None:
    """Emit a pipeline event; optional DEBUG log when ``QCHEM_PIPELINE_DEBUG_EVENTS=1``."""
    emit_pipeline_event(
        event_name,
        data=data or {},
        stage=stage,
        trace_id=trace_id,
    )
    if _debug_events_enabled():
        _log.debug("pipeline_event %s stage=%s trace_id=%s", event_name, stage, trace_id)


def trace_id_from_run_context(run_context: object | None) -> str | None:
    if run_context is None:
        return None
    tid = getattr(run_context, "trace_id", None)
    return str(tid) if tid is not None else None

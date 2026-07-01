"""Event-driven architecture for pipeline stage communication."""

from __future__ import annotations

import json
import logging

from qchem_stack.orchestration.pipeline_event_bus import EventBus
from qchem_stack.orchestration.pipeline_event_types import (
    EventHandler,
    EventPriority,
    PipelineEvent,
)

__all__ = [
    "EventBus",
    "EventHandler",
    "EventPriority",
    "PipelineEvent",
    "PipelineEvents",
    "emit_pipeline_event",
    "get_event_bus",
    "reset_event_bus",
]


class PipelineEvents:
    """Standard event names for pipeline stages."""

    SCF_STARTED = "stage.scf.started"
    SCF_COMPLETED = "stage.scf.completed"
    SCF_FAILED = "stage.scf.failed"

    PRE_QUANTUM_STARTED = "stage.pre_quantum.started"
    PRE_QUANTUM_COMPLETED = "stage.pre_quantum.completed"
    PRE_QUANTUM_FAILED = "stage.pre_quantum.failed"

    VARIATIONAL_STARTED = "stage.variational.started"
    VARIATIONAL_ITERATION = "stage.variational.iteration"
    VARIATIONAL_COMPLETED = "stage.variational.completed"
    VARIATIONAL_FAILED = "stage.variational.failed"

    EMBEDDING_WORKFLOW_STARTED = "stage.embedding_workflow.started"
    EMBEDDING_WORKFLOW_COMPLETED = "stage.embedding_workflow.completed"
    EMBEDDING_WORKFLOW_FAILED = "stage.embedding_workflow.failed"

    EXCITED_STARTED = "stage.excited.started"
    EXCITED_COMPLETED = "stage.excited.completed"
    EXCITED_FAILED = "stage.excited.failed"

    PROTOCOL_FINALIZE_STARTED = "stage.protocol_finalize.started"
    PROTOCOL_FINALIZE_COMPLETED = "stage.protocol_finalize.completed"
    PROTOCOL_FINALIZE_FAILED = "stage.protocol_finalize.failed"

    PIPELINE_STARTED = "pipeline.started"
    PIPELINE_COMPLETED = "pipeline.completed"
    PIPELINE_FAILED = "pipeline.failed"


_global_event_bus: EventBus | None = None
_default_subscribers_registered = False
_pipeline_event_log = logging.getLogger("qchem_stack.orchestration.pipeline_events")


def _log_pipeline_event(event: PipelineEvent) -> None:
    payload = {
        "schema": "pipeline_event_v1",
        "event": event.name,
        "stage": event.stage,
        "trace_id": event.trace_id,
    }
    if event.data:
        payload["data"] = event.data
    _pipeline_event_log.info("%s", json.dumps(payload, sort_keys=True))


def _register_default_subscribers(bus: EventBus) -> None:
    global _default_subscribers_registered
    if _default_subscribers_registered:
        return
    bus.subscribe("stage.*", _log_pipeline_event)
    bus.subscribe("pipeline.*", _log_pipeline_event)
    _default_subscribers_registered = True


def get_event_bus() -> EventBus:
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
        _register_default_subscribers(_global_event_bus)
        from qchem_stack.orchestration.pipeline_otel_subscriber import (
            register_otel_subscriber_if_configured,
        )

        register_otel_subscriber_if_configured(_global_event_bus)
    return _global_event_bus


def reset_event_bus() -> None:
    global _global_event_bus, _default_subscribers_registered
    _global_event_bus = None
    _default_subscribers_registered = False


def emit_pipeline_event(
    event_name: str,
    data: dict[str, object] | None = None,
    stage: str | None = None,
    trace_id: str | None = None,
    metadata: dict[str, object] | None = None,
) -> None:
    bus = get_event_bus()
    event = PipelineEvent(
        name=event_name,
        data=data or {},
        stage=stage,
        trace_id=trace_id,
        metadata=metadata or {},
    )
    bus.emit(event)

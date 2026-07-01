"""Optional OpenTelemetry OTLP subscriber for pipeline events (no core dependency)."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qchem_stack.orchestration.pipeline_event_types import PipelineEvent

_log = logging.getLogger(__name__)
_otel_registered = False


def _otel_available() -> bool:
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if not endpoint:
        return False
    try:
        import opentelemetry  # noqa: F401
    except ImportError:
        return False
    return True


def register_otel_subscriber_if_configured(bus: object) -> None:
    """Attach OTLP span exporter subscriber when observability extra + env are set."""
    global _otel_registered
    if _otel_registered or not _otel_available():
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
    except ImportError:
        _log.debug("observability extra not installed; skipping OTel subscriber")
        return

    resource = Resource.create({"service.name": "qchem-stack"})
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("qchem_stack.orchestration")

    def _export_event(event: PipelineEvent) -> None:
        with tracer.start_as_current_span(event.name) as span:
            if event.stage:
                span.set_attribute("pipeline.stage", event.stage)
            if event.trace_id:
                span.set_attribute("trace_id", event.trace_id)
            for key, val in (event.data or {}).items():
                span.set_attribute(f"pipeline.data.{key}", str(val))

    subscribe = getattr(bus, "subscribe", None)
    if callable(subscribe):
        subscribe("stage.*", _export_event)
        subscribe("pipeline.*", _export_event)
        _otel_registered = True
        _log.info("Registered OpenTelemetry OTLP subscriber for pipeline events")


__all__ = ["register_otel_subscriber_if_configured"]

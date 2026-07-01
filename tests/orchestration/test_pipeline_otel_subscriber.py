"""OpenTelemetry subscriber registration (optional extra)."""

from __future__ import annotations

import pytest

from qchem_stack.orchestration.pipeline_event_bus import EventBus
from qchem_stack.orchestration.pipeline_event_types import PipelineEvent
from qchem_stack.orchestration.pipeline_otel_subscriber import (
    register_otel_subscriber_if_configured,
)


def test_otel_subscriber_noop_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    bus = EventBus()
    register_otel_subscriber_if_configured(bus)
    bus.emit(PipelineEvent(name="stage.scf.started", data={}, stage="scf"))

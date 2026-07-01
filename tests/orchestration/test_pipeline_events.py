"""Unit tests for orchestration EventBus."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qchem_stack.orchestration.pipeline_events import (
    EventBus,
    EventPriority,
    PipelineEvent,
    PipelineEvents,
    reset_event_bus,
)


@pytest.fixture(autouse=True)
def _reset_global_bus() -> None:
    reset_event_bus()
    yield
    reset_event_bus()


def test_handler_priority_order() -> None:
    bus = EventBus()
    order: list[str] = []

    @bus.on("test.event", priority=EventPriority.LOW)
    def low(_: PipelineEvent) -> None:
        order.append("low")

    @bus.on("test.event", priority=EventPriority.CRITICAL)
    def critical(_: PipelineEvent) -> None:
        order.append("critical")

    bus.emit(PipelineEvent(name="test.event"))
    assert order == ["critical", "low"]


def test_wildcard_subscription() -> None:
    bus = EventBus()
    seen: list[str] = []

    @bus.on("stage.scf.*")
    def on_scf(event: PipelineEvent) -> None:
        seen.append(event.name)

    bus.emit(PipelineEvent(name="stage.scf.started"))
    bus.emit(PipelineEvent(name="stage.variational.completed"))
    assert seen == ["stage.scf.started"]


def test_once_handler_removed_after_first_emit() -> None:
    bus = EventBus()
    count = 0

    @bus.on("once.event", once=True)
    def once_handler(_: PipelineEvent) -> None:
        nonlocal count
        count += 1

    bus.emit(PipelineEvent(name="once.event"))
    bus.emit(PipelineEvent(name="once.event"))
    assert count == 1


def test_handler_exception_does_not_block_others() -> None:
    bus = EventBus()
    ok: list[str] = []

    @bus.on("fail.event")
    def fail(_: PipelineEvent) -> None:
        raise RuntimeError("boom")

    @bus.on("fail.event")
    def ok_handler(_: PipelineEvent) -> None:
        ok.append("ok")

    bus.emit(PipelineEvent(name="fail.event"))
    assert ok == ["ok"]


def test_pipeline_event_requires_name() -> None:
    with pytest.raises(ValueError, match="name cannot be empty"):
        PipelineEvent(name="")


def test_emit_stage_event_constants_exist() -> None:
    assert PipelineEvents.SCF_STARTED == "stage.scf.started"
    assert PipelineEvents.PIPELINE_COMPLETED == "pipeline.completed"


def test_otel_subscriber_noop_without_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    from qchem_stack.orchestration.pipeline_event_bus import EventBus
    from qchem_stack.orchestration.pipeline_otel_subscriber import (
        register_otel_subscriber_if_configured,
    )

    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    bus = EventBus()
    register_otel_subscriber_if_configured(bus)
    bus.emit(PipelineEvent(name="stage.scf.started", stage="scf"))


def test_otel_subscriber_registers_handlers_with_mocked_sdk(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import qchem_stack.orchestration.pipeline_otel_subscriber as mod
    from qchem_stack.orchestration.pipeline_event_bus import EventBus

    monkeypatch.setattr(mod, "_otel_registered", False)
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:4318")
    monkeypatch.setattr(mod, "_otel_available", lambda: True)

    class _Span:
        def set_attribute(self, _key: str, _val: str) -> None:
            return None

        def __enter__(self) -> _Span:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

    class _Tracer:
        def start_as_current_span(self, _name: str) -> _Span:
            return _Span()

    fake_trace = MagicMock()
    fake_trace.get_tracer.return_value = _Tracer()

    fake_otel = MagicMock()
    fake_exporter = MagicMock()
    fake_resource = MagicMock()
    fake_resource.create.return_value = MagicMock()
    fake_provider = MagicMock()
    fake_provider_cls = MagicMock(return_value=fake_provider)
    fake_processor = MagicMock()

    monkeypatch.setitem(
        __import__("sys").modules,
        "opentelemetry",
        fake_otel,
    )
    monkeypatch.setitem(__import__("sys").modules, "opentelemetry.trace", fake_trace)
    monkeypatch.setitem(
        __import__("sys").modules,
        "opentelemetry.exporter.otlp.proto.http.trace_exporter",
        MagicMock(OTLPSpanExporter=fake_exporter),
    )
    monkeypatch.setitem(
        __import__("sys").modules,
        "opentelemetry.sdk.resources",
        MagicMock(Resource=fake_resource),
    )
    monkeypatch.setitem(
        __import__("sys").modules,
        "opentelemetry.sdk.trace",
        MagicMock(TracerProvider=fake_provider_cls),
    )
    monkeypatch.setitem(
        __import__("sys").modules,
        "opentelemetry.sdk.trace.export",
        MagicMock(BatchSpanProcessor=fake_processor),
    )

    subscribed: list[str] = []
    bus = EventBus()

    def _capture_subscribe(name: str, handler: object, **kwargs: object) -> None:
        subscribed.append(name)

    monkeypatch.setattr(bus, "subscribe", _capture_subscribe)
    mod.register_otel_subscriber_if_configured(bus)
    assert "stage.*" in subscribed
    assert "pipeline.*" in subscribed

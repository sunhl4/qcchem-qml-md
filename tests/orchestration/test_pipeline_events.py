"""Unit tests for orchestration EventBus."""

from __future__ import annotations

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

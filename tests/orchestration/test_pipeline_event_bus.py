"""Unit tests for split pipeline event bus."""

from __future__ import annotations

from qchem_stack.orchestration.pipeline_event_bus import EventBus
from qchem_stack.orchestration.pipeline_event_types import EventPriority, PipelineEvent


def test_event_bus_subscribe_emit_and_history() -> None:
    bus = EventBus()
    seen: list[str] = []

    @bus.on("stage.scf.completed", priority=EventPriority.HIGH)
    def _handler(event: PipelineEvent) -> None:
        seen.append(event.name)

    bus.emit(PipelineEvent(name="stage.scf.completed", data={"energy": -1.0}))
    assert seen == ["stage.scf.completed"]
    hist = bus.get_history("stage.scf.*")
    assert len(hist) == 1
    bus.clear_history()
    assert bus.get_history() == []

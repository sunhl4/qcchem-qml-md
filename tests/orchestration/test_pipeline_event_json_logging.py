"""Pipeline event default subscriber emits structured JSON log lines."""

from __future__ import annotations

import json

from qchem_stack.orchestration import pipeline_events as pe
from qchem_stack.orchestration.pipeline_event_types import PipelineEvent
from qchem_stack.orchestration.pipeline_events import PipelineEvents


def test_log_pipeline_event_emits_json(monkeypatch) -> None:
    captured: list[tuple[str, tuple[object, ...]]] = []

    def _capture(msg: str, *args: object, **kwargs: object) -> None:
        captured.append((msg, args))

    monkeypatch.setattr(pe._pipeline_event_log, "info", _capture)
    pe._log_pipeline_event(
        PipelineEvent(
            name=PipelineEvents.SCF_COMPLETED,
            stage="scf",
            trace_id="trace-abc",
            data={"duration_ms": 12.5},
        )
    )
    assert captured
    msg, args = captured[0]
    raw = args[0] if args else msg
    payload = json.loads(str(raw))
    assert payload["schema"] == "pipeline_event_v1"
    assert payload["event"] == PipelineEvents.SCF_COMPLETED
    assert payload["stage"] == "scf"
    assert payload["trace_id"] == "trace-abc"
    assert payload["data"]["duration_ms"] == 12.5

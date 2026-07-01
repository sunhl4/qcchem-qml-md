"""Pipeline failure paths emit *_FAILED events and record repro.run_summary."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.pipeline_events import (
    PipelineEvents,
    get_event_bus,
    reset_event_bus,
)
from qchem_stack.orchestration.pipeline_sync_runner import _run_pipeline_stages
from qchem_stack.orchestration.stage_registry import StageLifecycle, StageSpec


def test_run_pipeline_stages_emits_failed_events(make_pipeline_context) -> None:
    reset_event_bus()
    bus = get_event_bus()
    ctx = make_pipeline_context()

    failing_spec = StageSpec(
        "scf",
        StageLifecycle(
            "scf",
            PipelineEvents.SCF_STARTED,
            PipelineEvents.SCF_COMPLETED,
            PipelineEvents.SCF_FAILED,
        ),
        MagicMock(side_effect=RuntimeError("scf boom")),
        post_run=None,
    )
    with (
        patch(
            "qchem_stack.orchestration.pipeline_sync_runner.PIPELINE_STAGE_SPECS",
            (failing_spec,),
        ),
        pytest.raises(PipelineError, match="stage scf failed"),
    ):
        _run_pipeline_stages(ctx)

    names = [e.name for e in bus.get_history()]
    assert PipelineEvents.SCF_FAILED in names
    assert PipelineEvents.PIPELINE_FAILED in names
    rs = ctx.repro.get("run_summary", {})
    assert rs.get("stage_failed") == "scf"
    assert rs.get("error_type") == "RuntimeError"
    reset_event_bus()

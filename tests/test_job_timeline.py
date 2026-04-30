"""Persisted job timeline (Nexus-style milestone analog)."""

from __future__ import annotations

import tempfile

from qchem_stack.jobs.pipeline_jobs import enqueue_full_pipeline_run
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.orchestration.run_context import RunContext


def test_timeline_submitted_then_running() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/tl.sqlite"
        store = SqliteJobStore(path)
        rc = RunContext.new()
        h = enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: t1\n",
            run_context=rc,
            meta_extra={"experiment_id": "t1"},
        )
        tl0 = store.get_job_timeline_events(h.job_id)
        assert tl0["source"] == "sqlite_timeline_json_v1"
        assert len(tl0["events"]) == 1
        assert tl0["events"][0]["kind"] == "submitted"

        store.mark_running(h.job_id)
        tl1 = store.get_job_timeline_events(h.job_id)
        assert len(tl1["events"]) == 2
        assert tl1["events"][-1]["kind"] == "running"

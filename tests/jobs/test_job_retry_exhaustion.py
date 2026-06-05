"""Job store retry bookkeeping when runner keeps failing."""

from __future__ import annotations

import tempfile
from typing import TYPE_CHECKING

import pytest

from qchem_stack.jobs.store import JobStatus, SqliteJobStore, process_job_with_retry

if TYPE_CHECKING:
    from qchem_stack.jobs.store_service import SqliteJobStore as Store


def _failing_runner(_store: Store, _job_id: str) -> None:
    raise RuntimeError("simulated pipeline failure")


def test_process_job_with_retry_marks_failed_after_max_retries() -> None:
    with tempfile.TemporaryDirectory() as d:
        store = SqliteJobStore(f"{d}/retry.sqlite")
        store.enqueue("job-retry-1", b"payload", protocol_hash="ph1")
        for _ in range(2):
            process_job_with_retry(
                store,
                "job-retry-1",
                _failing_runner,
                max_retries=1,
                already_running=False,
            )
        row = store.result("job-retry-1")
        assert row["status"] == JobStatus.FAILED.value
        assert int(row.get("retry_count") or 0) >= 1
        err = row.get("error_message") or row.get("error")
        assert err
        assert "simulated pipeline failure" in str(err)


def test_list_jobs_status_filter_excludes_failed_when_queued_requested() -> None:
    with tempfile.TemporaryDirectory() as d:
        store = SqliteJobStore(f"{d}/filter.sqlite")
        store.enqueue("q1", b"a", protocol_hash="h1")
        store.enqueue("q2", b"b", protocol_hash="h2")
        process_job_with_retry(store, "q1", _failing_runner, max_retries=0, already_running=False)
        queued = store.list_jobs(status=JobStatus.QUEUED.value, limit=10)
        failed = store.list_jobs(status=JobStatus.FAILED.value, limit=10)
        assert len(queued) == 1
        assert queued[0]["job_id"] == "q2"
        assert len(failed) == 1
        assert failed[0]["job_id"] == "q1"

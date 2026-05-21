"""Bounded retry runner for SQLite job store."""

from __future__ import annotations

import time
import traceback
from collections.abc import Callable
from typing import TYPE_CHECKING

from .store_schema import JobStatus

if TYPE_CHECKING:
    from .store_service import SqliteJobStore

JobRunner = Callable[["SqliteJobStore", str], None]


def process_job_with_retry(
    store: SqliteJobStore,
    job_id: str,
    runner: JobRunner,
    *,
    max_retries: int = 2,
    already_running: bool = False,
) -> None:
    """Run ``runner(store, job_id)`` with bounded retries before marking FAILED."""
    if not already_running:
        store.mark_running(job_id)
    try:
        runner(store, job_id)
    except Exception as e:  # pragma: no cover - exercised via test
        msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        con = store._connect()
        row = con.execute("SELECT retry_count FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        r = int(row[0] if row and row[0] is not None else 0)
        if r < max_retries:
            con.execute(
                """UPDATE jobs SET retry_count=retry_count+1, status=?, result=NULL,
                   error_message=?, updated=? WHERE job_id=?""",
                (JobStatus.QUEUED.value, msg[:8000], time.time(), job_id),
            )
        else:
            con.execute(
                "UPDATE jobs SET status=?, error_message=?, updated=? WHERE job_id=?",
                (JobStatus.FAILED.value, msg[:8000], time.time(), job_id),
            )
        con.commit()
        con.close()
        if r < max_retries:
            store.append_timeline(job_id, "retry_scheduled", JobStatus.QUEUED.value)
        else:
            store.append_timeline(job_id, "failed", JobStatus.FAILED.value)

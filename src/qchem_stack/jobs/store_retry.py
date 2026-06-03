"""Bounded retry runner for SQLite job store with exponential backoff."""

from __future__ import annotations

import sqlite3
import time
import traceback
from collections.abc import Callable
from typing import TYPE_CHECKING

from .store_schema import JobStatus

if TYPE_CHECKING:
    from .store_service import SqliteJobStore

JobRunner = Callable[["SqliteJobStore", str], None]

# Default exponential backoff parameters
DEFAULT_BASE_DELAY_S = 1.0
DEFAULT_MAX_DELAY_S = 60.0


def exponential_backoff_delay(
    retry_count: int,
    base_delay: float = DEFAULT_BASE_DELAY_S,
    max_delay: float = DEFAULT_MAX_DELAY_S,
) -> float:
    """Compute exponential backoff delay: ``min(base_delay * 2^retry_count, max_delay)``."""
    return min(base_delay * (2**retry_count), max_delay)


def process_job_with_retry(
    store: SqliteJobStore,
    job_id: str,
    runner: JobRunner,
    *,
    max_retries: int = 2,
    already_running: bool = False,
    exponential_backoff: bool = False,
    base_delay: float = DEFAULT_BASE_DELAY_S,
    max_delay: float = DEFAULT_MAX_DELAY_S,
) -> None:
    """Run ``runner(store, job_id)`` with bounded retries before marking FAILED.

    When ``exponential_backoff`` is True, the job is re-queued to QUEUED status
    but the worker will sleep for ``base_delay * 2^retry_count`` seconds before
    claiming it again (the delay is recorded in the ``updated`` column; the
    claim query filters out jobs whose ``updated + delay`` is still in the future).

    Without exponential backoff (default), the job is immediately re-queued.
    """
    if not already_running:
        store.mark_running(job_id)
    try:
        runner(store, job_id)
    except sqlite3.Error:
        raise
    except Exception as e:
        msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        con = store._connect()
        row = con.execute("SELECT retry_count FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        r = int(row[0] if row and row[0] is not None else 0)
        if r < max_retries:
            if exponential_backoff:
                delay = exponential_backoff_delay(r, base_delay, max_delay)
                # Set updated to now + delay so claim_next_queued skips it
                updated_at = time.time() + delay
                con.execute(
                    """UPDATE jobs SET retry_count=retry_count+1, status=?, result=NULL,
                       error_message=?, updated=? WHERE job_id=?""",
                    (JobStatus.QUEUED.value, msg[:8000], updated_at, job_id),
                )
            else:
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

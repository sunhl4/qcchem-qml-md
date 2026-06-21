"""Bounded retry runner for job stores with exponential backoff."""

from __future__ import annotations

import traceback
from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .store_schema import WorkerJobStore

JobRunner = Callable[["WorkerJobStore", str], None]

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
    store: WorkerJobStore,
    job_id: str,
    runner: JobRunner,
    *,
    max_retries: int = 2,
    already_running: bool = False,
    exponential_backoff: bool = False,
    base_delay: float = DEFAULT_BASE_DELAY_S,
    max_delay: float = DEFAULT_MAX_DELAY_S,
) -> None:
    """Run ``runner(store, job_id)`` with bounded retries before marking FAILED."""
    if not already_running:
        store.mark_running(job_id)
    try:
        runner(store, job_id)
    except Exception as e:
        msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        store.requeue_after_failure(
            job_id,
            msg,
            max_retries=max_retries,
            exponential_backoff=exponential_backoff,
            base_delay=base_delay,
            max_delay=max_delay,
        )

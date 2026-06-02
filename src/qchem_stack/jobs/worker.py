from __future__ import annotations

import argparse
import logging
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

from qchem_stack.jobs.store import SqliteJobStore, process_job_with_retry
from qchem_stack.jobs.worker_dispatch import dispatch_job

Runner = Callable[[SqliteJobStore, str], None]

logger = logging.getLogger(__name__)


def drain_one_queued(
    store: SqliteJobStore,
    runner: Runner | None = None,
    *,
    max_retries: int = 2,
    timeout_seconds: int | None = None,
) -> bool:
    """If a ``QUEUED`` job exists, run ``runner`` with retry bookkeeping; return whether one was processed.

    Args:
        store: Job store instance
        runner: Job runner function (defaults to dispatch_job)
        max_retries: Maximum retry attempts before marking FAILED
        timeout_seconds: Maximum execution time per job (None = no timeout)

    Returns:
        True if a job was processed, False if queue was empty
    """
    jid = store.claim_next_queued()
    if jid is None:
        return False
    fn = runner if runner is not None else dispatch_job

    if timeout_seconds is not None:
        # Create cancellation event for cooperative cancellation
        cancel_event = threading.Event()

        # Wrap runner to check cancellation
        def cancellable_runner(store: SqliteJobStore, job_id: str) -> None:
            if cancel_event.is_set():
                raise RuntimeError(f"Job {job_id} was cancelled")
            fn(store, job_id)

        # Execute with timeout using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1, thread_name_prefix="job") as executor:
            future = executor.submit(
                process_job_with_retry,
                store,
                jid,
                cancellable_runner,
                max_retries=max_retries,
                already_running=True,
            )
            try:
                future.result(timeout=timeout_seconds)
            except FutureTimeoutError:
                logger.error(f"Job {jid} timed out after {timeout_seconds}s")
                store.mark_timed_out(jid, timeout_seconds)
                # Signal cooperative cancellation
                cancel_event.set()
                # Best-effort cancel (only works if not yet started)
                future.cancel()
                # Shutdown without waiting to avoid blocking on hung thread
                executor.shutdown(wait=False, cancel_futures=True)
    else:
        process_job_with_retry(store, jid, fn, max_retries=max_retries, already_running=True)
    return True


def worker_loop(
    store: SqliteJobStore,
    sleep_interval: float,
    max_retries: int,
    worker_id: int,
) -> None:
    """Polling loop for a single worker thread.

    Continuously claims and processes jobs, sleeping when queue is empty.
    """
    logger.info(f"Worker {worker_id} started")
    while True:
        if not drain_one_queued(
            store,
            dispatch_job,
            max_retries=max_retries,
        ):
            time.sleep(sleep_interval)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Poll SQLite job store: Pauli protocol (pickle) and full_pipeline (YAML) jobs.",
    )
    ap.add_argument("--db", type=str, required=True, help="Path to jobs.sqlite")
    ap.add_argument("--sleep", type=float, default=0.5, help="Seconds to wait when queue is empty")
    ap.add_argument("--max-retries", type=int, default=2)
    ap.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of concurrent worker threads (default: 1)",
    )
    args = ap.parse_args()

    store = SqliteJobStore(args.db)

    if args.workers <= 1:
        # Single worker: run in main thread (backward compatible)
        worker_loop(store, args.sleep, args.max_retries, worker_id=0)
    else:
        # Multiple workers: use thread pool
        logger.info(f"Starting {args.workers} concurrent workers")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = []
            for i in range(args.workers):
                future = executor.submit(
                    worker_loop,
                    store,
                    args.sleep,
                    args.max_retries,
                    worker_id=i,
                )
                futures.append(future)

            # Wait for all workers (they run indefinitely)
            for future in futures:
                future.result()


if __name__ == "__main__":
    main()

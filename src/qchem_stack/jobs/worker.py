from __future__ import annotations

import argparse
import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import TYPE_CHECKING

from qchem_stack.jobs.store_factory import job_store_from_cli
from qchem_stack.jobs.store_retry import JobRunner, process_job_with_retry
from qchem_stack.jobs.worker_dispatch import dispatch_job

if TYPE_CHECKING:
    from qchem_stack.jobs.store_schema import WorkerJobStore

logger = logging.getLogger(__name__)


def drain_one_queued(
    store: WorkerJobStore,
    runner: JobRunner | None = None,
    *,
    max_retries: int = 2,
    timeout_seconds: int | None = None,
) -> bool:
    """If a ``QUEUED`` job exists, run ``runner`` with retry bookkeeping; return whether one was processed."""
    jid = store.claim_next_queued()
    if jid is None:
        return False
    fn = runner if runner is not None else dispatch_job

    if timeout_seconds is not None:
        cancel_event = threading.Event()

        def cancellable_runner(store: WorkerJobStore, job_id: str) -> None:
            if cancel_event.is_set():
                raise RuntimeError(f"Job {job_id} was cancelled")
            fn(store, job_id)

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
                logger.error("Job %s timed out after %ss", jid, timeout_seconds)
                store.mark_timed_out(jid, timeout_seconds)
                cancel_event.set()
                future.cancel()
                executor.shutdown(wait=False, cancel_futures=True)
    else:
        process_job_with_retry(store, jid, fn, max_retries=max_retries, already_running=True)
    return True


def worker_loop(
    store: WorkerJobStore,
    sleep_interval: float,
    max_retries: int,
    worker_id: int,
) -> None:
    """Polling loop for a single worker thread."""
    logger.info("Worker %s started", worker_id)
    while True:
        if not drain_one_queued(
            store,
            dispatch_job,
            max_retries=max_retries,
        ):
            time.sleep(sleep_interval)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Poll job store: Pauli protocol (pickle) and full_pipeline (YAML) jobs.",
    )
    ap.add_argument("--db", type=str, default=None, help="Path to jobs.sqlite (SQLite backend)")
    ap.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Postgres DSN (overrides --db; also reads QCHEM_JOB_DATABASE_URL)",
    )
    ap.add_argument("--sleep", type=float, default=0.5, help="Seconds to wait when queue is empty")
    ap.add_argument("--max-retries", type=int, default=2)
    ap.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of concurrent worker threads (default: 1)",
    )
    args = ap.parse_args()

    if os.environ.get("QCHEM_PROTOCOL_BLOB_V2", "1").strip().lower() in {"0", "false", "no", "off"}:
        logger.warning(
            "QCHEM_PROTOCOL_BLOB_V2=0 writes legacy signed pickle v1; "
            "this path is deprecated and will be removed in 1.1."
        )

    store = job_store_from_cli(db_path=args.db, db_url=args.db_url)

    if args.workers <= 1:
        worker_loop(store, args.sleep, args.max_retries, worker_id=0)
    else:
        logger.info("Starting %s concurrent workers", args.workers)
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
            for future in futures:
                future.result()


if __name__ == "__main__":
    main()

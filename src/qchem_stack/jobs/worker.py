from __future__ import annotations

import argparse
import time
from collections.abc import Callable

from qchem_stack.jobs.store import SqliteJobStore, process_job_with_retry
from qchem_stack.jobs.worker_dispatch import dispatch_job

Runner = Callable[[SqliteJobStore, str], None]


def drain_one_queued(
    store: SqliteJobStore,
    runner: Runner | None = None,
    *,
    max_retries: int = 2,
) -> bool:
    """If a ``QUEUED`` job exists, run ``runner`` with retry bookkeeping; return whether one was processed."""
    jid = store.fetch_next_queued()
    if jid is None:
        return False
    fn = runner if runner is not None else dispatch_job
    process_job_with_retry(store, jid, fn, max_retries=max_retries)
    return True


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Poll SQLite job store: Pauli protocol (pickle) and full_pipeline (YAML) jobs.",
    )
    ap.add_argument("--db", type=str, required=True, help="Path to jobs.sqlite")
    ap.add_argument("--sleep", type=float, default=0.5, help="Seconds to wait when queue is empty")
    ap.add_argument("--max-retries", type=int, default=2)
    args = ap.parse_args()

    store = SqliteJobStore(args.db)
    while True:
        if not drain_one_queued(
            store,
            dispatch_job,
            max_retries=args.max_retries,
        ):
            time.sleep(args.sleep)


if __name__ == "__main__":
    main()

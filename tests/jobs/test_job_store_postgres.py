"""Postgres JobStore integration tests (requires QCHEM_JOB_DATABASE_URL)."""

from __future__ import annotations

import os
import threading

import pytest

pytest.importorskip("psycopg")

from qchem_stack.jobs.store_postgres import PostgresJobStore

pytestmark = pytest.mark.skipif(
    not os.environ.get("QCHEM_JOB_DATABASE_URL"),
    reason="QCHEM_JOB_DATABASE_URL not set",
)


def test_postgres_enqueue_complete(pg_store: PostgresJobStore) -> None:
    pg_store.enqueue("pg-e2e-1", b"yaml-bytes")
    jid = pg_store.claim_next_queued()
    assert jid == "pg-e2e-1"
    pg_store.complete("pg-e2e-1", {"energy": -1.0})
    out = pg_store.result("pg-e2e-1")
    assert out["status"] == "DONE"
    assert out["energy"] == -1.0


def test_postgres_concurrent_claim_unique(pg_store: PostgresJobStore) -> None:
    for i in range(4):
        pg_store.enqueue(f"pg-conc-{i}", b"p")
    claimed: list[str | None] = []

    def _claim() -> None:
        claimed.append(pg_store.claim_next_queued())

    threads = [threading.Thread(target=_claim) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    ids = [c for c in claimed if c is not None]
    assert len(ids) == len(set(ids))
    assert len(ids) >= 1

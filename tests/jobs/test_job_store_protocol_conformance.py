"""Job store protocol conformance for Memory, SQLite, and optional Postgres."""

from __future__ import annotations

import inspect
import os
import uuid

import pytest

from qchem_stack.jobs.store import InMemoryJobStore, SqliteJobStore
from qchem_stack.jobs.store_schema import WorkerJobStore

_WORKER_METHODS = (
    "enqueue",
    "result",
    "claim_next_queued",
    "mark_running",
    "complete",
    "fail",
    "append_timeline",
    "get_job_public_summary",
    "get_job_row",
    "requeue_after_failure",
)


def _assert_worker_surface(store: WorkerJobStore) -> None:
    for name in _WORKER_METHODS:
        assert hasattr(store, name)
        assert callable(getattr(store, name))


@pytest.fixture
def memory_store() -> InMemoryJobStore:
    return InMemoryJobStore()


@pytest.fixture
def sqlite_store(tmp_path) -> SqliteJobStore:
    return SqliteJobStore(tmp_path / "jobs.sqlite")


@pytest.fixture
def postgres_store():
    url = os.environ.get("QCHEM_JOB_DATABASE_URL")
    if not url:
        pytest.skip("QCHEM_JOB_DATABASE_URL not set")
    from qchem_stack.jobs.store_postgres import PostgresJobStore

    return PostgresJobStore(url)


def test_inmemory_enqueue_and_result(memory_store: InMemoryJobStore) -> None:
    _assert_worker_surface(memory_store)
    memory_store.enqueue("j1", b"payload", protocol_hash="abc")
    row = memory_store.result("j1")
    assert row["status"] == "QUEUED"


def test_sqlite_claim_and_complete(sqlite_store: SqliteJobStore) -> None:
    _assert_worker_surface(sqlite_store)
    sqlite_store.enqueue("j2", b"payload")
    claimed = sqlite_store.claim_next_queued()
    assert claimed == "j2"
    sqlite_store.complete("j2", {"ok": True})
    out = sqlite_store.result("j2")
    assert out["status"] == "DONE"
    assert out["ok"] is True


@pytest.mark.parametrize(
    "store_fixture",
    ["memory_store", "sqlite_store", "postgres_store"],
)
def test_requeue_after_failure(store_fixture: str, request: pytest.FixtureRequest) -> None:
    store: WorkerJobStore = request.getfixturevalue(store_fixture)
    job_id = f"requeue-{store_fixture}-{uuid.uuid4().hex[:8]}"
    store.enqueue(job_id, b"x")
    store.mark_running(job_id)
    scheduled = store.requeue_after_failure(job_id, "boom", max_retries=2)
    assert scheduled is True
    assert store.result(job_id)["status"] == "QUEUED"


@pytest.mark.parametrize(
    "store_fixture",
    ["memory_store", "sqlite_store", "postgres_store"],
)
def test_append_timeline(store_fixture: str, request: pytest.FixtureRequest) -> None:
    store: WorkerJobStore = request.getfixturevalue(store_fixture)
    job_id = f"timeline-{store_fixture}-{uuid.uuid4().hex[:8]}"
    store.enqueue(job_id, b"p")
    store.append_timeline(job_id, "test_marker", "QUEUED")
    summary = store.get_job_public_summary(job_id)
    assert summary is not None
    assert summary["status"] == "QUEUED"


def test_postgres_claim_smoke(postgres_store) -> None:
    _assert_worker_surface(postgres_store)
    job_id = f"pg-smoke-{uuid.uuid4().hex[:8]}"
    postgres_store.enqueue(job_id, b"payload")
    claimed = postgres_store.claim_next_queued()
    assert claimed == job_id
    postgres_store.complete(job_id, {"schema": "ok"})


def test_enqueue_signature_matches_protocol() -> None:
    sig = inspect.signature(SqliteJobStore.enqueue)
    params = list(sig.parameters.keys())
    assert params[0] == "self"
    assert "job_id" in params
    assert "payload" in params

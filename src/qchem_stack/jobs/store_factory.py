"""Factory helpers for job store backends."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from .store_memory import InMemoryJobStore
from .store_service import SqliteJobStore

if TYPE_CHECKING:
    from .store_schema import WorkerJobStore


def job_store_from_cli(*, db_path: str | None, db_url: str | None) -> WorkerJobStore:
    """Resolve a worker-compatible store from CLI flags or environment."""
    if db_url:
        from .store_postgres import PostgresJobStore

        return PostgresJobStore(db_url)
    env_url = os.environ.get("QCHEM_JOB_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if env_url and not db_path:
        from .store_postgres import PostgresJobStore

        return PostgresJobStore(env_url)
    if db_path is None:
        raise ValueError("either --db (SQLite path) or --db-url (Postgres DSN) is required")
    return SqliteJobStore(db_path)


def in_memory_job_store() -> InMemoryJobStore:
    return InMemoryJobStore()


__all__ = ["SqliteJobStore", "in_memory_job_store", "job_store_from_cli"]

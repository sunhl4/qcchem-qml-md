"""SQLite-backed job ledger service (core + mixin composition)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .store_lifecycle import JobStoreLifecycleMixin
from .store_queries import JobStoreQueriesMixin
from .store_retry import JobRunner, process_job_with_retry
from .store_schema import (
    DEFAULT_JOB_KIND,
    JobHandle,
    JobStatus,
    parse_meta_json,
)
from .store_sql import (
    JOBS_CREATE_TABLE_SQL,
    connect_sqlite,
    dump_timeline_events,
    ensure_jobs_indexes,
    migrate_jobs_schema,
    set_startup_pragmas,
)
from .store_timeline import JobStoreTimelineMixin

__all__ = ["JobRunner", "SqliteJobStore", "process_job_with_retry"]


class SqliteJobStore(
    JobStoreTimelineMixin,
    JobStoreLifecycleMixin,
    JobStoreQueriesMixin,
):
    """Async job ledger with retries, failures, and JSON results.

    Supports both connection-per-operation (default) and persistent connection modes.
    Use as a context manager for persistent connection:

        with SqliteJobStore(path) as store:
            store.enqueue(...)
            store.get_job_row(...)
    """

    def __init__(self, path: str | Path, *, persistent: bool = False) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._persistent = persistent
        self._conn = None

        # Initialize schema
        con = self._connect()
        try:
            set_startup_pragmas(con)
            con.execute(JOBS_CREATE_TABLE_SQL)
            migrate_jobs_schema(con)
            ensure_jobs_indexes(con)
            con.commit()
            if persistent:
                self._conn = con  # Keep connection open
            else:
                con.close()
        except Exception:
            con.close()
            raise

    def _connect(self):
        return connect_sqlite(str(self.path))

    def __enter__(self):
        """Enter context manager - ensure persistent connection."""
        if not self._persistent:
            self._persistent = True
            if self._conn is None:
                self._conn = self._connect()
                set_startup_pragmas(self._conn)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> bool:
        """Exit context manager - close persistent connection."""
        self.close()
        return False

    def close(self):
        """Close the persistent connection if open."""
        if self._conn is not None:
            try:
                self._conn.close()
            finally:
                self._conn = None
                self._persistent = False

    def _get_connection(self):
        """Get a connection for operations - persistent or new."""
        if self._persistent and self._conn is not None:
            return self._conn, False  # connection, is_temporary
        return self._connect(), True  # new connection, is_temporary

    def enqueue(
        self,
        job_id: str,
        payload: bytes,
        protocol_hash: str | None = None,
        *,
        job_kind: str = DEFAULT_JOB_KIND,
        meta: dict[str, Any] | None = None,
    ) -> JobHandle:
        con, is_temp = self._get_connection()
        try:
            now = time.time()
            meta_s = json.dumps(meta, sort_keys=True) if meta is not None else None
            initial_timeline = dump_timeline_events(
                [{"t": now, "kind": "submitted", "status": JobStatus.QUEUED.value}]
            )
            con.execute(
                """INSERT OR REPLACE INTO jobs
                (job_id, payload, status, result, created, updated, retry_count, error_message,
                 protocol_hash, job_kind, meta, timeline_json)
                VALUES (?,?,?,?,?,?,0,NULL,?,?,?,?)""",
                (
                    job_id,
                    payload,
                    JobStatus.QUEUED.value,
                    None,
                    now,
                    now,
                    protocol_hash,
                    job_kind,
                    meta_s,
                    initial_timeline,
                ),
            )
            con.commit()
        finally:
            if is_temp:
                con.close()
        return JobHandle(job_id=job_id, protocol_hash=protocol_hash)

    def get_job_row(self, job_id: str) -> dict[str, Any]:
        con, is_temp = self._get_connection()
        try:
            row = con.execute(
                "SELECT payload, job_kind, meta, protocol_hash, status FROM jobs WHERE job_id=?",
                (job_id,),
            ).fetchone()
        finally:
            if is_temp:
                con.close()
        if row is None:
            raise KeyError(job_id)
        payload, jk, meta_raw, ph, st = row
        return {
            "payload": payload,
            "job_kind": jk or DEFAULT_JOB_KIND,
            "meta": parse_meta_json(meta_raw),
            "protocol_hash": ph,
            "status": st,
        }

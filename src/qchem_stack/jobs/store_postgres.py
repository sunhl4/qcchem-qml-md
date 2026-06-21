"""Postgres-backed job ledger (production reference for multi-worker deployments)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import JOB_TIMELINE_V1

if TYPE_CHECKING:
    from psycopg import Connection as PgConnection

from .store_retry import exponential_backoff_delay
from .store_schema import (
    DEFAULT_JOB_KIND,
    JobHandle,
    JobListItem,
    JobPublicSummary,
    JobStatus,
    JobTimelineResponse,
    parse_meta_json,
)
from .store_sql import dump_timeline_events, load_timeline_events, rows_to_list_items

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - optional extra
    psycopg = None  # type: ignore[assignment]
    dict_row = None  # type: ignore[assignment,misc]


def _require_psycopg() -> None:
    if psycopg is None:
        raise ImportError(
            "PostgresJobStore requires psycopg; install with pip install 'qchem-stack[jobs-postgres]'"
        )


def _schema_ddl() -> str:
    root = Path(__file__).resolve().parents[3]
    sql_path = root / "scripts" / "init_postgres_jobs.sql"
    if not sql_path.is_file():
        raise RuntimeError(f"Postgres schema file missing: {sql_path}")
    return sql_path.read_text(encoding="utf-8")


class PostgresJobStore:
    """Postgres job ledger with atomic claim for concurrent workers."""

    def __init__(self, conninfo: str) -> None:
        self._conninfo = conninfo
        self._ensure_schema()

    def _connect(self) -> PgConnection:
        _require_psycopg()
        return psycopg.connect(self._conninfo, row_factory=dict_row)  # type: ignore[union-attr]

    def _ensure_schema(self) -> None:
        con = self._connect()
        try:
            con.execute(_schema_ddl())
            con.commit()
        finally:
            con.close()

    def enqueue(
        self,
        job_id: str,
        payload: bytes,
        protocol_hash: str | None = None,
        *,
        job_kind: str = DEFAULT_JOB_KIND,
        meta: dict[str, Any] | None = None,
    ) -> JobHandle:
        now = time.time()
        meta_s = json.dumps(meta, sort_keys=True) if meta is not None else None
        initial_timeline = dump_timeline_events(
            [{"t": now, "kind": "submitted", "status": JobStatus.QUEUED.value}]
        )
        con = self._connect()
        try:
            con.execute(
                """INSERT INTO jobs
                (job_id, payload, status, result, created, updated, retry_count, error_message,
                 protocol_hash, job_kind, meta, timeline_json)
                VALUES (%s,%s,%s,NULL,%s,%s,0,NULL,%s,%s,%s,%s)
                ON CONFLICT (job_id) DO UPDATE SET
                  payload=EXCLUDED.payload, status=EXCLUDED.status, result=NULL,
                  updated=EXCLUDED.updated, retry_count=0, error_message=NULL,
                  protocol_hash=EXCLUDED.protocol_hash, job_kind=EXCLUDED.job_kind,
                  meta=EXCLUDED.meta, timeline_json=EXCLUDED.timeline_json""",
                (
                    job_id,
                    payload,
                    JobStatus.QUEUED.value,
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
            con.close()
        return JobHandle(job_id=job_id, protocol_hash=protocol_hash)

    def get_job_row(self, job_id: str) -> dict[str, Any]:
        con = self._connect()
        try:
            row = con.execute(
                "SELECT payload, job_kind, meta, protocol_hash, status FROM jobs WHERE job_id=%s",
                (job_id,),
            ).fetchone()
        finally:
            con.close()
        if row is None:
            raise KeyError(job_id)
        return {
            "payload": row["payload"],
            "job_kind": row["job_kind"] or DEFAULT_JOB_KIND,
            "meta": parse_meta_json(row["meta"]),
            "protocol_hash": row["protocol_hash"],
            "status": row["status"],
        }

    def mark_running(self, job_id: str) -> None:
        con = self._connect()
        try:
            con.execute(
                "UPDATE jobs SET status=%s, updated=%s WHERE job_id=%s",
                (JobStatus.RUNNING.value, time.time(), job_id),
            )
            con.commit()
        finally:
            con.close()
        self.append_timeline(job_id, "running", JobStatus.RUNNING.value)

    def complete(self, job_id: str, result: dict[str, Any]) -> None:
        con = self._connect()
        try:
            con.execute(
                "UPDATE jobs SET status=%s, result=%s, error_message=NULL, updated=%s WHERE job_id=%s",
                (JobStatus.DONE.value, json.dumps(result), time.time(), job_id),
            )
            con.commit()
        finally:
            con.close()
        self.append_timeline(job_id, "completed", JobStatus.DONE.value)

    def fail(self, job_id: str, message: str) -> None:
        con = self._connect()
        try:
            con.execute(
                "UPDATE jobs SET status=%s, error_message=%s, updated=%s WHERE job_id=%s",
                (JobStatus.FAILED.value, message[:8000], time.time(), job_id),
            )
            con.commit()
        finally:
            con.close()
        self.append_timeline(job_id, "failed", JobStatus.FAILED.value)

    def mark_timed_out(self, job_id: str, timeout_seconds: int) -> None:
        message = f"Job exceeded timeout limit of {timeout_seconds} seconds"
        con = self._connect()
        try:
            con.execute(
                "UPDATE jobs SET status=%s, error_message=%s, updated=%s WHERE job_id=%s",
                (JobStatus.TIMED_OUT.value, message, time.time(), job_id),
            )
            con.commit()
        finally:
            con.close()
        self.append_timeline(job_id, "timed_out", JobStatus.TIMED_OUT.value)

    def append_timeline(self, job_id: str, kind: str, status: str) -> None:
        self.append_timeline_event(job_id, {"kind": kind, "status": status})

    def get_job_timeline_events(self, job_id: str) -> JobTimelineResponse:
        con = self._connect()
        try:
            row = con.execute(
                "SELECT timeline_json, created, updated, status FROM jobs WHERE job_id=%s",
                (job_id,),
            ).fetchone()
        finally:
            con.close()
        if row is None:
            raise KeyError(job_id)
        events = load_timeline_events(row["timeline_json"])
        if events:
            return {
                "schema": JOB_TIMELINE_V1,
                "source": "postgres_timeline_json_v1",
                "events": events,
            }
        return {
            "schema": JOB_TIMELINE_V1,
            "source": "postgres_coarse_timeline_v1",
            "events": [
                {
                    "t": float(row["created"]) if row["created"] is not None else 0.0,
                    "kind": "submitted",
                    "status": JobStatus.QUEUED.value,
                },
                {
                    "t": float(row["updated"]) if row["updated"] is not None else 0.0,
                    "kind": "state_snapshot",
                    "status": str(row["status"]),
                },
            ],
        }

    def claim_next_queued(self) -> str | None:
        con = self._connect()
        now = time.time()
        job_id: str | None = None
        try:
            row = con.execute(
                """UPDATE jobs SET status=%s, updated=%s
                   WHERE job_id = (
                     SELECT job_id FROM jobs
                     WHERE status=%s AND updated <= %s
                     ORDER BY created ASC LIMIT 1
                     FOR UPDATE SKIP LOCKED
                   )
                   RETURNING job_id""",
                (JobStatus.RUNNING.value, now, JobStatus.QUEUED.value, now),
            ).fetchone()
            con.commit()
            if row is not None:
                job_id = str(row["job_id"])
        finally:
            con.close()
        if job_id is not None:
            self.append_timeline(job_id, "running", JobStatus.RUNNING.value)
        return job_id

    def result(self, job_id: str) -> dict[str, Any]:
        con = self._connect()
        try:
            row = con.execute(
                """SELECT status, result, error_message, retry_count, job_kind, meta
                   FROM jobs WHERE job_id=%s""",
                (job_id,),
            ).fetchone()
        finally:
            con.close()
        if row is None:
            raise KeyError(job_id)
        out: dict[str, Any] = {
            "status": row["status"],
            "retry_count": int(row["retry_count"] or 0),
            "job_kind": row["job_kind"] or DEFAULT_JOB_KIND,
        }
        meta_obj = parse_meta_json(row["meta"])
        if meta_obj is not None:
            out["meta"] = meta_obj
        if row["error_message"]:
            out["error"] = row["error_message"]
        if row["status"] == JobStatus.DONE.value and row["result"] is not None:
            out.update(json.loads(row["result"]))
        return out

    def get_job_public_summary(self, job_id: str) -> JobPublicSummary:
        con = self._connect()
        try:
            row = con.execute(
                """SELECT status, job_kind, created, updated, meta, retry_count, error_message
                   FROM jobs WHERE job_id=%s""",
                (job_id,),
            ).fetchone()
        finally:
            con.close()
        if row is None:
            raise KeyError(job_id)
        out: JobPublicSummary = {
            "job_id": job_id,
            "status": str(row["status"]),
            "job_kind": row["job_kind"] or DEFAULT_JOB_KIND,
            "created": float(row["created"]) if row["created"] is not None else None,
            "updated": float(row["updated"]) if row["updated"] is not None else None,
            "retry_count": int(row["retry_count"] or 0),
        }
        meta_obj = parse_meta_json(row["meta"])
        if meta_obj is not None:
            out["meta"] = meta_obj
        if row["error_message"]:
            out["error"] = str(row["error_message"])[:2000]
        return out

    def requeue_after_failure(
        self,
        job_id: str,
        message: str,
        *,
        max_retries: int,
        exponential_backoff: bool = False,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ) -> bool:
        con = self._connect()
        scheduled = False
        try:
            row = con.execute("SELECT retry_count FROM jobs WHERE job_id=%s", (job_id,)).fetchone()
            r = int(row["retry_count"] if row and row["retry_count"] is not None else 0)
            now = time.time()
            if r < max_retries:
                updated_at = (
                    now + exponential_backoff_delay(r, base_delay, max_delay)
                    if exponential_backoff
                    else now
                )
                con.execute(
                    """UPDATE jobs SET retry_count=retry_count+1, status=%s, result=NULL,
                       error_message=%s, updated=%s WHERE job_id=%s""",
                    (JobStatus.QUEUED.value, message[:8000], updated_at, job_id),
                )
                scheduled = True
            else:
                con.execute(
                    "UPDATE jobs SET status=%s, error_message=%s, updated=%s WHERE job_id=%s",
                    (JobStatus.FAILED.value, message[:8000], now, job_id),
                )
            con.commit()
        finally:
            con.close()
        if scheduled:
            self.append_timeline(job_id, "retry_scheduled", JobStatus.QUEUED.value)
        else:
            self.append_timeline(job_id, "failed", JobStatus.FAILED.value)
        return scheduled

    def append_timeline_event(self, job_id: str, event: dict[str, Any]) -> None:
        con = self._connect()
        try:
            row = con.execute(
                "SELECT timeline_json FROM jobs WHERE job_id=%s", (job_id,)
            ).fetchone()
            if row is None:
                raise KeyError(job_id)
            events = load_timeline_events(row["timeline_json"])
            entry = dict(event)
            if "t" not in entry:
                entry["t"] = time.time()
            events.append(entry)
            con.execute(
                "UPDATE jobs SET timeline_json=%s WHERE job_id=%s",
                (dump_timeline_events(events), job_id),
            )
            con.commit()
        finally:
            con.close()

    def count_by_status(self) -> dict[str, int]:
        con = self._connect()
        try:
            rows = con.execute("SELECT status, COUNT(*) AS n FROM jobs GROUP BY status").fetchall()
        finally:
            con.close()
        return {str(r["status"]): int(r["n"]) for r in rows}

    def list_jobs(
        self,
        *,
        status: str | None = None,
        job_kind: str | None = None,
        experiment_id: str | None = None,
        api_workspace_label: str | None = None,
        api_project_slug: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[JobListItem]:
        lim = max(1, min(int(limit), 500))
        off = max(0, min(int(offset), 10_000))
        clauses: list[str] = []
        params: list[Any] = []
        if status is not None:
            clauses.append("status=%s")
            params.append(status)
        if job_kind is not None:
            clauses.append("job_kind=%s")
            params.append(job_kind)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        con = self._connect()
        try:
            rows = con.execute(
                f"""SELECT job_id, status, job_kind, created, updated, protocol_hash, meta
                    FROM jobs {where} ORDER BY created DESC LIMIT %s OFFSET %s""",
                [*params, lim, off],
            ).fetchall()
        finally:
            con.close()
        tuples = [
            (
                r["job_id"],
                r["status"],
                r["job_kind"],
                r["created"],
                r["updated"],
                r["protocol_hash"],
                r["meta"],
            )
            for r in rows
        ]
        items = rows_to_list_items(tuples)
        if experiment_id or api_workspace_label or api_project_slug:
            filtered = []
            for item in items:
                meta = item.get("meta") or {}
                if experiment_id and meta.get("experiment_id") != experiment_id:
                    continue
                if api_workspace_label and meta.get("api_workspace_label") != api_workspace_label:
                    continue
                if api_project_slug and meta.get("api_project_slug") != api_project_slug:
                    continue
                filtered.append(item)
            return filtered
        return items


def postgres_job_store_from_env() -> PostgresJobStore:
    import os

    url = os.environ.get("QCHEM_JOB_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("QCHEM_JOB_DATABASE_URL or DATABASE_URL required for PostgresJobStore")
    return PostgresJobStore(url)


__all__ = ["PostgresJobStore", "postgres_job_store_from_env"]

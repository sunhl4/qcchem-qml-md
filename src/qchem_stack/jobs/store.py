from __future__ import annotations

import json
import sqlite3
import time
import traceback
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Protocol

_JSON_SCAN_CAP = 5000


def _meta_top_str(meta_raw: str | None, key: str) -> str | None:
    if not meta_raw or not key:
        return None
    try:
        d = json.loads(meta_raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(d, dict):
        return None
    v = d.get(key)
    return str(v) if v is not None else None


def _meta_experiment_id_from_raw(meta_raw: str | None) -> str | None:
    return _meta_top_str(meta_raw, "experiment_id")


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class JobHandle:
    job_id: str
    protocol_hash: str | None = None
    """SHA-256 digest (hex prefix) of pickled protocol; matches DB `jobs.protocol_hash` when set."""


class JobStore(Protocol):
    def enqueue(self, job_id: str, payload: bytes, protocol_hash: str | None = None) -> JobHandle: ...
    def result(self, job_id: str) -> dict[str, Any]: ...


def _migrate_jobs_schema(con: sqlite3.Connection) -> None:
    cols = {row[1] for row in con.execute("PRAGMA table_info(jobs)").fetchall()}
    if "retry_count" not in cols:
        con.execute("ALTER TABLE jobs ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 0")
    if "error_message" not in cols:
        con.execute("ALTER TABLE jobs ADD COLUMN error_message TEXT")
    if "protocol_hash" not in cols:
        con.execute("ALTER TABLE jobs ADD COLUMN protocol_hash TEXT")
    if "job_kind" not in cols:
        con.execute("ALTER TABLE jobs ADD COLUMN job_kind TEXT NOT NULL DEFAULT 'pauli_protocol'")
    if "meta" not in cols:
        con.execute("ALTER TABLE jobs ADD COLUMN meta TEXT")
    if "timeline_json" not in cols:
        con.execute("ALTER TABLE jobs ADD COLUMN timeline_json TEXT")


class SqliteJobStore:
    """Async job ledger with retries, failures, and JSON results."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.path)
        con.execute(
            """CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                payload BLOB,
                status TEXT,
                result TEXT,
                created REAL,
                updated REAL,
                retry_count INTEGER NOT NULL DEFAULT 0,
                error_message TEXT,
                protocol_hash TEXT,
                job_kind TEXT NOT NULL DEFAULT 'pauli_protocol',
                meta TEXT,
                timeline_json TEXT
            )"""
        )
        _migrate_jobs_schema(con)
        con.commit()
        con.close()

    def enqueue(
        self,
        job_id: str,
        payload: bytes,
        protocol_hash: str | None = None,
        *,
        job_kind: str = "pauli_protocol",
        meta: dict[str, Any] | None = None,
    ) -> JobHandle:
        con = sqlite3.connect(self.path)
        now = time.time()
        meta_s = json.dumps(meta, sort_keys=True) if meta is not None else None
        initial_timeline = json.dumps(
            [{"t": now, "kind": "submitted", "status": JobStatus.QUEUED.value}],
            ensure_ascii=False,
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
        con.close()
        return JobHandle(job_id=job_id, protocol_hash=protocol_hash)

    def get_job_row(self, job_id: str) -> dict[str, Any]:
        con = sqlite3.connect(self.path)
        row = con.execute(
            "SELECT payload, job_kind, meta, protocol_hash, status FROM jobs WHERE job_id=?",
            (job_id,),
        ).fetchone()
        con.close()
        if row is None:
            raise KeyError(job_id)
        payload, jk, meta_raw, ph, st = row
        meta_obj: dict[str, Any] | None = None
        if meta_raw:
            try:
                meta_obj = json.loads(meta_raw)
            except json.JSONDecodeError:
                meta_obj = None
        return {
            "payload": payload,
            "job_kind": jk or "pauli_protocol",
            "meta": meta_obj,
            "protocol_hash": ph,
            "status": st,
        }

    def append_timeline_event(self, job_id: str, event: dict[str, Any]) -> None:
        """Append one timeline entry (JSON object). Adds ``t`` if missing."""
        con = sqlite3.connect(self.path)
        row = con.execute("SELECT timeline_json FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            con.close()
            raise KeyError(job_id)
        raw = row[0]
        events: list[Any] = []
        if raw:
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    events = parsed
            except json.JSONDecodeError:
                events = []
        entry = dict(event)
        if "t" not in entry:
            entry["t"] = time.time()
        events.append(entry)
        con.execute(
            "UPDATE jobs SET timeline_json=? WHERE job_id=?",
            (json.dumps(events, ensure_ascii=False), job_id),
        )
        con.commit()
        con.close()

    def append_timeline(self, job_id: str, kind: str, status: str) -> None:
        """Append one Nexus-style milestone (open analog; persisted when ``timeline_json`` column exists)."""
        self.append_timeline_event(job_id, {"kind": kind, "status": status})

    def get_job_timeline_events(self, job_id: str) -> dict[str, Any]:
        """Timeline for ``GET .../events`` — persisted JSON or coarse fallback for legacy rows."""
        con = sqlite3.connect(self.path)
        row = con.execute(
            "SELECT timeline_json, created, updated, status FROM jobs WHERE job_id=?",
            (job_id,),
        ).fetchone()
        con.close()
        if row is None:
            raise KeyError(job_id)
        raw, created, updated, status = row
        if raw:
            try:
                ev = json.loads(raw)
                if isinstance(ev, list) and ev:
                    return {
                        "schema": "job_timeline_v1",
                        "source": "sqlite_timeline_json_v1",
                        "events": ev,
                    }
            except json.JSONDecodeError:
                pass
        events_fb: list[dict[str, Any]] = [
            {"t": float(created) if created is not None else 0.0, "kind": "submitted", "status": JobStatus.QUEUED.value},
            {
                "t": float(updated) if updated is not None else 0.0,
                "kind": "state_snapshot",
                "status": str(status),
            },
        ]
        return {"schema": "job_timeline_v1", "source": "sqlite_coarse_timeline_v1", "events": events_fb}

    def mark_running(self, job_id: str) -> None:
        con = sqlite3.connect(self.path)
        con.execute(
            "UPDATE jobs SET status=?, updated=? WHERE job_id=?",
            (JobStatus.RUNNING.value, time.time(), job_id),
        )
        con.commit()
        con.close()
        self.append_timeline(job_id, "running", JobStatus.RUNNING.value)

    def complete(self, job_id: str, result: dict[str, Any]) -> None:
        con = sqlite3.connect(self.path)
        con.execute(
            "UPDATE jobs SET status=?, result=?, error_message=NULL, updated=? WHERE job_id=?",
            (JobStatus.DONE.value, json.dumps(result), time.time(), job_id),
        )
        con.commit()
        con.close()
        self.append_timeline(job_id, "completed", JobStatus.DONE.value)

    def fail(self, job_id: str, message: str) -> None:
        con = sqlite3.connect(self.path)
        con.execute(
            "UPDATE jobs SET status=?, error_message=?, updated=? WHERE job_id=?",
            (JobStatus.FAILED.value, message[:8000], time.time(), job_id),
        )
        con.commit()
        con.close()
        self.append_timeline(job_id, "failed", JobStatus.FAILED.value)

    def fetch_next_queued(self) -> str | None:
        con = sqlite3.connect(self.path)
        row = con.execute(
            "SELECT job_id FROM jobs WHERE status=? ORDER BY created ASC LIMIT 1",
            (JobStatus.QUEUED.value,),
        ).fetchone()
        con.close()
        return str(row[0]) if row else None

    def result(self, job_id: str) -> dict[str, Any]:
        con = sqlite3.connect(self.path)
        row = con.execute(
            """SELECT status, result, error_message, retry_count, job_kind, meta
               FROM jobs WHERE job_id=?""",
            (job_id,),
        ).fetchone()
        con.close()
        if row is None:
            raise KeyError(job_id)
        status, res, err, retries, job_kind, meta_raw = row
        out: dict[str, Any] = {
            "status": status,
            "retry_count": int(retries or 0),
            "job_kind": (job_kind or "pauli_protocol"),
        }
        if meta_raw:
            try:
                out["meta"] = json.loads(meta_raw)
            except json.JSONDecodeError:
                out["meta"] = None
        if err:
            out["error"] = err
        if status == JobStatus.DONE.value and res is not None:
            out.update(json.loads(res))
        return out

    def get_job_public_summary(self, job_id: str) -> dict[str, Any]:
        """Small row for polling: timestamps, status, ``meta`` — no payload or full ``result`` blob."""
        con = sqlite3.connect(self.path)
        row = con.execute(
            """SELECT status, job_kind, created, updated, meta, retry_count, error_message
               FROM jobs WHERE job_id=?""",
            (job_id,),
        ).fetchone()
        con.close()
        if row is None:
            raise KeyError(job_id)
        st, jk, created, updated, meta_raw, retries, err = row
        meta_obj: dict[str, Any] | None = None
        if meta_raw:
            try:
                meta_obj = json.loads(meta_raw)
            except json.JSONDecodeError:
                meta_obj = None
        out: dict[str, Any] = {
            "job_id": job_id,
            "status": st,
            "job_kind": jk or "pauli_protocol",
            "created": float(created) if created is not None else None,
            "updated": float(updated) if updated is not None else None,
            "retry_count": int(retries or 0),
        }
        if meta_obj is not None:
            out["meta"] = meta_obj
        if err:
            out["error"] = str(err)[:2000]
        return out

    def count_by_status(self) -> dict[str, int]:
        """Row counts per :class:`JobStatus` (missing statuses are omitted)."""
        con = sqlite3.connect(self.path)
        rows = con.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall()
        con.close()
        return {str(st): int(n) for st, n in rows}

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
    ) -> list[dict[str, Any]]:
        """Recent jobs (newest ``created`` first). For workspace / gateway listing."""
        lim = max(1, min(int(limit), 500))
        off = max(0, min(int(offset), 10_000))
        clauses: list[str] = []
        params: list[Any] = []
        if status is not None:
            clauses.append("status=?")
            params.append(status)
        if job_kind is not None:
            clauses.append("job_kind=?")
            params.append(job_kind)

        meta_eq: list[tuple[str, str]] = []
        if experiment_id is not None:
            meta_eq.append(("experiment_id", experiment_id))
        if api_workspace_label is not None:
            meta_eq.append(("api_workspace_label", api_workspace_label))
        if api_project_slug is not None:
            meta_eq.append(("api_project_slug", api_project_slug))

        def _rows_to_items(rows: list[Any]) -> list[dict[str, Any]]:
            out: list[dict[str, Any]] = []
            for job_id, st, jk, created, updated, ph, meta_raw in rows:
                item: dict[str, Any] = {
                    "job_id": str(job_id),
                    "status": st,
                    "job_kind": jk or "pauli_protocol",
                    "created": float(created) if created is not None else None,
                    "updated": float(updated) if updated is not None else None,
                }
                if ph:
                    item["protocol_hash"] = ph
                if meta_raw:
                    try:
                        item["meta"] = json.loads(meta_raw)
                    except json.JSONDecodeError:
                        item["meta"] = None
                out.append(item)
            return out

        where_base = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        con = sqlite3.connect(self.path)
        try:
            if not meta_eq:
                sql = (
                    f"SELECT job_id, status, job_kind, created, updated, protocol_hash, meta "
                    f"FROM jobs {where_base} ORDER BY created DESC, rowid DESC LIMIT ? OFFSET ?"
                )
                rows = con.execute(sql, [*params, lim, off]).fetchall()
                return _rows_to_items(rows)

            json_parts = [f"json_extract(meta, '$.{k}') = ?" for k, _ in meta_eq]
            exp_clauses = [*clauses, *json_parts]
            exp_params = [*params, *[v for _, v in meta_eq]]
            where_exp = f"WHERE {' AND '.join(exp_clauses)}"
            sql_json = (
                f"SELECT job_id, status, job_kind, created, updated, protocol_hash, meta "
                f"FROM jobs {where_exp} ORDER BY created DESC, rowid DESC LIMIT ? OFFSET ?"
            )
            try:
                rows = con.execute(sql_json, [*exp_params, lim, off]).fetchall()
                return _rows_to_items(rows)
            except sqlite3.OperationalError:
                scan_n = min(lim + off + 500, _JSON_SCAN_CAP)
                scan_sql = (
                    f"SELECT job_id, status, job_kind, created, updated, protocol_hash, meta "
                    f"FROM jobs {where_base} ORDER BY created DESC, rowid DESC LIMIT ?"
                )
                scanned = con.execute(scan_sql, [*params, scan_n]).fetchall()

                def _row_matches(r: Any) -> bool:
                    meta_raw = r[6]
                    return all(_meta_top_str(meta_raw, k) == v for k, v in meta_eq)

                filtered = [r for r in scanned if _row_matches(r)]
                slice_rows = filtered[off : off + lim]
                return _rows_to_items(slice_rows)
        finally:
            con.close()


def process_job_with_retry(
    store: SqliteJobStore,
    job_id: str,
    runner: Any,
    *,
    max_retries: int = 2,
) -> None:
    """
    Run ``runner(store, job_id)``; on failure increment ``retry_count`` and return to ``QUEUED``
    until ``max_retries`` attempts, then ``FAILED``.
    """
    store.mark_running(job_id)
    try:
        runner(store, job_id)
    except Exception as e:  # pragma: no cover - exercised via test
        msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
        con = sqlite3.connect(store.path)
        row = con.execute("SELECT retry_count FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        r = int(row[0] if row and row[0] is not None else 0)
        if r < max_retries:
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

"""SQLite schema, pragmas, and row-mapping helpers for the job ledger."""

from __future__ import annotations

import contextlib
import json
import sqlite3
from typing import Any

from .store_schema import DEFAULT_JOB_KIND, JobListItem, parse_meta_json

JSON_SCAN_CAP = 5000
SQLITE_BUSY_TIMEOUT_MS = 30_000

JOBS_CREATE_TABLE_SQL = """CREATE TABLE IF NOT EXISTS jobs (
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


def migrate_jobs_schema(con: sqlite3.Connection) -> None:
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


def ensure_jobs_indexes(con: sqlite3.Connection) -> None:
    con.execute("CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs(status, created ASC)")
    con.execute(
        "CREATE INDEX IF NOT EXISTS idx_jobs_job_kind_created ON jobs(job_kind, created DESC)"
    )


def connect_sqlite(
    path: str, *, busy_timeout_ms: int = SQLITE_BUSY_TIMEOUT_MS
) -> sqlite3.Connection:
    con = sqlite3.connect(path, timeout=busy_timeout_ms / 1000.0)
    con.execute(f"PRAGMA busy_timeout={busy_timeout_ms}")
    return con


def set_startup_pragmas(con: sqlite3.Connection) -> None:
    with contextlib.suppress(sqlite3.OperationalError):
        con.execute("PRAGMA journal_mode=WAL")
    with contextlib.suppress(sqlite3.OperationalError):
        con.execute("PRAGMA synchronous=NORMAL")


def rows_to_list_items(rows: list[Any]) -> list[JobListItem]:
    out: list[JobListItem] = []
    for job_id, st, jk, created, updated, ph, meta_raw in rows:
        item: JobListItem = {
            "job_id": str(job_id),
            "status": str(st),
            "job_kind": jk or DEFAULT_JOB_KIND,
            "created": float(created) if created is not None else None,
            "updated": float(updated) if updated is not None else None,
        }
        if ph:
            item["protocol_hash"] = str(ph)
        if meta_raw:
            item["meta"] = parse_meta_json(str(meta_raw))
        out.append(item)
    return out


def dump_timeline_events(events: list[Any]) -> str:
    return json.dumps(events, ensure_ascii=False)


def load_timeline_events(raw: str | None) -> list[Any]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []

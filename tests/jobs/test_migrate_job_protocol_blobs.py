"""Smoke tests for legacy protocol blob migration scanner."""

from __future__ import annotations

import pickle
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "migrate_job_protocol_blobs.py"


def _make_jobs_db(path: Path, *, legacy: bool) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, payload BLOB)")
        payload = pickle.dumps({"probe": True}, protocol=pickle.HIGHEST_PROTOCOL)
        if not legacy:
            payload = b"\x00" * 32 + payload
        conn.execute("INSERT INTO jobs (payload) VALUES (?)", (payload,))
        conn.commit()
    finally:
        conn.close()


def test_migrate_script_dry_run_counts_legacy(tmp_path: Path) -> None:
    db = tmp_path / "jobs.sqlite"
    _make_jobs_db(db, legacy=True)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--db", str(db)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "legacy_unsigned_pickle: 1" in proc.stdout


def test_migrate_script_missing_db_exits_nonzero(tmp_path: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--db", str(tmp_path / "missing.sqlite")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 1

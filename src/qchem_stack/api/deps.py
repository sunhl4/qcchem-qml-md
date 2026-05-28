"""Shared FastAPI dependencies and request helpers."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from fastapi import HTTPException
from pydantic import ValidationError

from qchem_stack.config import ExperimentConfig
from qchem_stack.jobs.store import SqliteJobStore

if TYPE_CHECKING:
    from qchem_stack.orchestration.run_context import RunContext


def default_job_db_path() -> Path:
    env = os.environ.get("QCHEM_JOB_DB")
    if env:
        return Path(env)
    return Path(tempfile.gettempdir()) / "qchem_api_jobs.sqlite"


def sqlite_job_store(job_db_path: str | None = None) -> SqliteJobStore:
    db = Path(job_db_path) if job_db_path else default_job_db_path()
    return SqliteJobStore(db)


def experiment_config_from_request_yaml(
    experiment_yaml: str,
    *,
    config_base_dir: str | None = None,
) -> ExperimentConfig:
    try:
        raw = yaml.safe_load(experiment_yaml)
    except yaml.YAMLError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise HTTPException(status_code=400, detail="experiment_yaml must parse to a mapping")
    base_dir = None
    if config_base_dir is not None and config_base_dir.strip():
        base_dir = Path(config_base_dir).expanduser().resolve()
    try:
        return ExperimentConfig.from_yaml_dict(raw, geometry_files_base_dir=base_dir)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc


def trace_response_headers(rc: RunContext) -> dict[str, str]:
    headers: dict[str, str] = {"X-Trace-ID": rc.trace_id}
    if rc.client_request_id:
        headers["X-Request-ID"] = rc.client_request_id
    return headers


def ping_job_db(path: Path) -> None:
    """Raise HTTPException 503 when the default job DB path is not usable.

    This is a read-only check that does not create directories or database files.
    """
    if not path.exists():
        # Database doesn't exist yet, but that's okay - it will be created on first use
        return

    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        con.execute("SELECT 1").fetchone()
        con.close()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail=f"Job DB not readable: {exc}") from exc

"""
Minimal HTTP surface for synchronous runs and async SQLite-backed queue.

Bind to ``127.0.0.1`` in production behind a reverse proxy; add authentication
before exposing on a network interface.
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError

from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import QChemStackError
from qchem_stack.jobs.pipeline_jobs import enqueue_full_pipeline_run
from qchem_stack.jobs.pipeline_runner import pipeline_result_for_job_store
from qchem_stack.jobs.store import JobStatus, SqliteJobStore
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.orchestration.run_context import RunContext
from qchem_stack.integrations.inquanto_workflow_preview import (
    slim_product_summary_from_pipeline_result,
    workflow_preview_payload,
)
from qchem_stack.protocols.computable import computables_export_dict, list_computables_for_config

app = FastAPI(
    title="qchem-stack",
    version="0.1.0",
    description="Local API + SQLite queue analog to cloud submit/poll; parity metadata mirrors docs/inquanto_public_parity_matrix.md.",
    openapi_tags=[
        {"name": "health", "description": "Liveness and readiness probes."},
        {"name": "meta", "description": "Product / parity metadata for dashboards."},
        {
            "name": "product",
            "description": "InQuanto-public-docs-shaped UX (workflow stages, computable graph) — open analog only.",
        },
        {"name": "runs", "description": "Submit experiments and poll SQLite-backed jobs."},
    ],
)


def default_job_db_path() -> Path:
    env = os.environ.get("QCHEM_JOB_DB")
    if env:
        return Path(env)
    return Path(tempfile.gettempdir()) / "qchem_api_jobs.sqlite"


class RunRequest(BaseModel):
    experiment_yaml: str = Field(..., description="Full experiment YAML (same as CLI configs)")
    sync: bool = Field(
        default=False,
        description="If true, run in-process and return full_pipeline_job_result_v1 (JSON-safe slim dict, same as async DONE payload)",
    )
    job_db_path: str | None = Field(default=None, description="SQLite path for queued jobs; default from QCHEM_JOB_DB or temp")
    workspace_label: str | None = Field(
        default=None,
        description="Optional Nexus-style project/workspace string stored in job meta (api_workspace_label)",
    )
    project_slug: str | None = Field(
        default=None,
        description="Optional Nexus/organization project slug stored in meta (api_project_slug); pairs with workspace for listing",
    )


class YamlPreviewBody(BaseModel):
    experiment_yaml: str = Field(..., description="YAML to validate; returns computable list without running chemistry")
    include_computables_rich: bool = Field(
        default=False,
        description="Optional parallel field: adds computables_rich (schema computables_rich_v1) without removing computable_abstract",
    )


def experiment_config_from_request_yaml(experiment_yaml: str) -> ExperimentConfig:
    """Parse YAML and build :class:`ExperimentConfig`; raises :class:`HTTPException` on failure."""
    try:
        raw = yaml.safe_load(experiment_yaml)
    except yaml.YAMLError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise HTTPException(status_code=400, detail="experiment_yaml must parse to a mapping")
    try:
        return ExperimentConfig.from_yaml_dict(raw)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc


def _trace_response_headers(rc: RunContext) -> dict[str, str]:
    h: dict[str, str] = {"X-Trace-ID": rc.trace_id}
    if rc.client_request_id:
        h["X-Request-ID"] = rc.client_request_id
    return h


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
def ready() -> dict[str, str]:
    """Check default job DB path is usable (mkdir + SQLite ping). Returns 503 on I/O failure."""
    p = default_job_db_path()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        store = SqliteJobStore(p)
        con = sqlite3.connect(store.path)
        con.execute("SELECT 1").fetchone()
        con.close()
    except (OSError, sqlite3.Error) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ready", "job_db_default": str(p.resolve())}


@app.get("/v1/meta/product-analog", tags=["product"])
def product_analog() -> dict[str, object]:
    """
    Single call for consoles: what this open API emulates vs InQuanto/Nexus *public* narratives.

    Closed-source binaries are not described here — only our designed L1 analog surface.
    """
    from qchem_stack import __version__

    return {
        "schema": "product_analog_v1",
        "qchem_stack_version": __version__,
        "emulation_notes": [
            "Five-stage protocol preview: POST /v1/meta/workflow-preview (YAML-only, no chemistry).",
            "Computable DAG (semantic v2): POST /v1/meta/workflow-preview.",
            "Capability one-shot: GET /v1/meta/capability-surface (gaps + public object map).",
            "Job lifecycle: POST/GET /v1/runs (optional project_slug), GET /v1/runs/{id}/summary, repro GET /v1/runs/{id}/repro (DONE only); events use persisted timeline when available.",
        ],
        "gap_export": "/v1/meta/parity-gaps",
        "capability_surface": "/v1/meta/capability-surface",
    }


@app.get("/v1/meta/capability-surface", tags=["meta"])
def capability_surface() -> dict[str, object]:
    """
    Single fetch for landing / admin consoles: version, full gap rows, InQuanto-public name → implementation map.

    **Not** a substitute for narrative docs — aggregates machine-readable parity artifacts.
    """
    from qchem_stack import __version__
    from qchem_stack.protocols.inquanto_contract import (
        inquanto_gap_categories,
        inquanto_object_map_for_docs,
        mitigation_execution_model_public,
        open_stack_differentiators_public,
    )

    return {
        "schema": "capability_surface_v1",
        "qchem_stack_version": __version__,
        "object_map": inquanto_object_map_for_docs(),
        "gaps": inquanto_gap_categories(),
        "mitigation_execution_model": mitigation_execution_model_public(),
        "open_stack_differentiators": open_stack_differentiators_public(),
    }


@app.get("/v1/meta/parity-gaps", tags=["meta"])
def parity_gaps() -> dict[str, object]:
    """Machine-readable gap list vs InQuanto public docs (dashboards / regression tooling)."""
    from qchem_stack import __version__
    from qchem_stack.protocols.inquanto_contract import inquanto_gap_categories

    return {
        "schema": "inquanto_gap_export_v1",
        "qchem_stack_version": __version__,
        "gaps": inquanto_gap_categories(),
    }


@app.post("/v1/meta/workflow-preview", tags=["product"])
def workflow_preview(body: YamlPreviewBody) -> dict[str, object]:
    """
    InQuanto-style **protocol stage** checklist + **computable DAG** from YAML alone (instantiate→evaluate).

    Use before submit to drive a Nexus-like wizard or notebook cell summary.
    """
    cfg = experiment_config_from_request_yaml(body.experiment_yaml)
    return workflow_preview_payload(cfg, include_computables_rich=body.include_computables_rich)


@app.post("/v1/meta/computables-preview", tags=["meta"])
def computables_preview(body: YamlPreviewBody) -> dict[str, object]:
    """InQuanto-style **Computable** list + ``computable_abstract`` v2 from YAML only (no PySCF run)."""
    cfg = experiment_config_from_request_yaml(body.experiment_yaml)
    refs = list_computables_for_config(cfg)
    return {
        "schema": "computables_preview_v1",
        "experiment_id": cfg.experiment_id,
        "computables": [{"name": r.name, "kind": r.kind, "details": r.details} for r in refs],
        "computable_abstract": computables_export_dict(cfg, protocol_counts=None),
    }


@app.get("/v1/meta/queue-stats", tags=["meta"])
def queue_stats(
    job_db_path: str | None = Query(default=None, description="SQLite path; default QCHEM_JOB_DB or temp"),
) -> dict[str, object]:
    """Per-status job counts (ops dashboard analog)."""
    db = Path(job_db_path) if job_db_path else default_job_db_path()
    store = SqliteJobStore(db)
    counts = store.count_by_status()
    return {
        "schema": "queue_stats_v1",
        "job_db": str(db.resolve()),
        "counts": counts,
    }


@app.get("/v1/runs", tags=["runs"])
def list_runs(
    job_db_path: str | None = Query(default=None, description="SQLite path; default QCHEM_JOB_DB or temp"),
    status: str | None = Query(default=None, description="Filter: QUEUED, RUNNING, DONE, FAILED"),
    job_kind: str | None = Query(default=None, description="Filter e.g. full_pipeline, pauli_protocol"),
    experiment_id: str | None = Query(
        default=None,
        description="Filter jobs whose store meta JSON contains this experiment_id",
    ),
    api_workspace_label: str | None = Query(
        default=None,
        description="Filter by meta.api_workspace_label (POST workspace_label)",
    ),
    api_project_slug: str | None = Query(
        default=None,
        description="Filter by meta.api_project_slug (POST project_slug)",
    ),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0, le=10_000, description="Skip N newest rows (pagination)"),
) -> dict[str, object]:
    if status is not None and status not in {s.value for s in JobStatus}:
        raise HTTPException(
            status_code=400,
            detail=f"invalid status {status!r}; use one of {[s.value for s in JobStatus]}",
        )
    db = Path(job_db_path) if job_db_path else default_job_db_path()
    store = SqliteJobStore(db)
    jobs = store.list_jobs(
        status=status,
        job_kind=job_kind,
        experiment_id=experiment_id,
        api_workspace_label=api_workspace_label,
        api_project_slug=api_project_slug,
        limit=limit,
        offset=offset,
    )
    return {
        "schema": "job_list_v1",
        "job_db": str(db.resolve()),
        "limit": limit,
        "offset": offset,
        "jobs": jobs,
    }


@app.post("/v1/runs", response_model=None, tags=["runs"])
def post_run(request: Request, body: RunRequest) -> dict | JSONResponse:
    rc = RunContext.from_headers({str(k): str(v) for k, v in request.headers.items()})
    cfg = experiment_config_from_request_yaml(body.experiment_yaml)
    headers = _trace_response_headers(rc)
    if body.sync:
        try:
            out = run_pipeline_sync(cfg, cfg_path=None, run_context=rc)
        except QChemStackError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return JSONResponse(pipeline_result_for_job_store(out), headers=headers)

    meta_extra: dict[str, Any] = {"experiment_id": cfg.experiment_id}
    na = cfg.nexus_analog
    if na.enabled and na.project_label:
        meta_extra["nexus_analog_project_label"] = str(na.project_label)
    if body.workspace_label and str(body.workspace_label).strip():
        meta_extra["api_workspace_label"] = str(body.workspace_label).strip()[:400]
    if body.project_slug and str(body.project_slug).strip():
        meta_extra["api_project_slug"] = str(body.project_slug).strip()[:200]

    db = Path(body.job_db_path) if body.job_db_path else default_job_db_path()
    store = SqliteJobStore(db)
    handle = enqueue_full_pipeline_run(
        store,
        config_yaml=body.experiment_yaml,
        run_context=rc,
        meta_extra=meta_extra,
    )
    return JSONResponse(
        {
            "schema": "run_enqueue_response_v1",
            "job_id": handle.job_id,
            "experiment_id": cfg.experiment_id,
            "trace_id": rc.trace_id,
            "client_request_id": rc.client_request_id,
            "status": "QUEUED",
            "job_db": str(db.resolve()),
        },
        status_code=202,
        headers=headers,
    )


@app.get("/v1/runs/{job_id}/status", tags=["runs"])
def get_run_status(
    job_id: str,
    job_db_path: str | None = Query(default=None, description="Must match enqueue DB"),
) -> dict[str, object]:
    db = Path(job_db_path) if job_db_path else default_job_db_path()
    store = SqliteJobStore(db)
    try:
        summary = store.get_job_public_summary(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"job not found: {e}") from e
    return {"schema": "job_status_v1", **summary}


@app.get("/v1/runs/{job_id}/events", tags=["runs"])
def get_run_events(
    job_id: str,
    job_db_path: str | None = Query(default=None, description="Must match enqueue DB"),
) -> dict[str, object]:
    db = Path(job_db_path) if job_db_path else default_job_db_path()
    store = SqliteJobStore(db)
    try:
        tl = store.get_job_timeline_events(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"job not found: {e}") from e
    events_raw = tl.get("events") or []
    events: list[dict[str, object]] = [dict(e) for e in events_raw if isinstance(e, dict)]
    return {
        "schema": "job_events_v1",
        "job_id": job_id,
        "note": str(tl.get("source", "")),
        "events": events,
    }


@app.get("/v1/runs/{job_id}/summary", tags=["runs"])
def get_run_summary_ux(
    job_id: str,
    job_db_path: str | None = Query(default=None, description="Must match enqueue DB"),
) -> dict[str, object]:
    """
    **Product slim** summary: key energies, ``run_summary`` excerpt, sidecar flags — for dashboards.

    Unlike ``GET /v1/runs/{id}/repro``, available semantics: **200** for any status; ``partial=true`` until DONE.
    """
    db = Path(job_db_path) if job_db_path else default_job_db_path()
    store = SqliteJobStore(db)
    try:
        row = store.result(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"job not found: {e}") from e
    slim = slim_product_summary_from_pipeline_result(row)
    slim["job_id"] = job_id
    return slim


@app.get("/v1/runs/{job_id}/repro", tags=["runs"])
def get_run_repro(
    job_id: str,
    job_db_path: str | None = Query(default=None, description="Must match enqueue DB"),
) -> dict[str, object]:
    """``repro`` JSON only when ``status=DONE`` (Methods / strict export); **409** while queued or running."""
    db = Path(job_db_path) if job_db_path else default_job_db_path()
    store = SqliteJobStore(db)
    try:
        row = store.result(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"job not found: {e}") from e
    st = row.get("status")
    if st != JobStatus.DONE.value:
        raise HTTPException(
            status_code=409,
            detail={"message": "repro available when job status is DONE", "status": st},
        )
    repro = row.get("repro")
    if not isinstance(repro, dict):
        raise HTTPException(status_code=404, detail="result has no repro block")
    return {"schema": "run_repro_only_v1", "job_id": job_id, "job_kind": row.get("job_kind"), "repro": repro}


@app.get("/v1/runs/{job_id}", tags=["runs"])
def get_run(
    job_id: str,
    job_db_path: str | None = Query(default=None, description="Must match the DB used when enqueueing"),
) -> dict:
    db = Path(job_db_path) if job_db_path else default_job_db_path()
    store = SqliteJobStore(db)
    try:
        return store.result(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"job not found: {e}") from e

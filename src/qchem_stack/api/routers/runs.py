from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from qchem_stack.api.deps import (
    default_job_db_path,
    experiment_config_from_request_yaml,
    sqlite_job_store,
    trace_response_headers,
)
from qchem_stack.api.middleware import RUNS_GET_LIMIT, RUNS_POST_LIMIT, rate_limit
from qchem_stack.api.models import RunRequest
from qchem_stack.contracts.schema_ids import (
    JOB_EVENTS_V1,
    JOB_LIST_V1,
    JOB_STATUS_V1,
    RUN_ENQUEUE_RESPONSE_V1,
    RUN_REPRO_ONLY_V1,
)
from qchem_stack.exceptions import QChemStackError
from qchem_stack.integrations.workflow_preview import slim_product_summary_from_pipeline_result
from qchem_stack.jobs.pipeline_jobs import enqueue_full_pipeline_run
from qchem_stack.jobs.pipeline_runner import pipeline_result_for_job_store
from qchem_stack.jobs.store import JobStatus
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.orchestration.run_context import RunContext

router = APIRouter(tags=["runs"])


@router.get("/v1/runs")
@rate_limit(RUNS_GET_LIMIT)
def list_runs(
    request: Request,
    job_db_path: str | None = Query(
        default=None, description="SQLite path; default QCHEM_JOB_DB or temp"
    ),
    status: str | None = Query(default=None, description="Filter: QUEUED, RUNNING, DONE, FAILED"),
    job_kind: str | None = Query(
        default=None, description="Filter e.g. full_pipeline, pauli_protocol"
    ),
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
    store = sqlite_job_store(str(db))
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
        "schema": JOB_LIST_V1,
        "job_db": str(db.resolve()),
        "limit": limit,
        "offset": offset,
        "jobs": jobs,
    }


@router.post("/v1/runs", response_model=None)
@rate_limit(RUNS_POST_LIMIT)
def post_run(request: Request, body: Annotated[RunRequest, Body()]) -> dict | JSONResponse:
    rc = RunContext.from_headers({str(k): str(v) for k, v in request.headers.items()})
    cfg = experiment_config_from_request_yaml(
        body.experiment_yaml,
        config_base_dir=body.config_base_dir,
    )
    headers = trace_response_headers(rc)
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
    store = sqlite_job_store(str(db))
    handle = enqueue_full_pipeline_run(
        store,
        config_yaml=body.experiment_yaml,
        config_base_dir=body.config_base_dir,
        run_context=rc,
        meta_extra=meta_extra,
    )
    return JSONResponse(
        {
            "schema": RUN_ENQUEUE_RESPONSE_V1,
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


@router.get("/v1/runs/{job_id}/status")
def get_run_status(
    job_id: str,
    job_db_path: str | None = Query(default=None, description="Must match enqueue DB"),
) -> dict[str, object]:
    store = sqlite_job_store(job_db_path)
    try:
        summary = store.get_job_public_summary(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"job not found: {e}") from e
    return {"schema": JOB_STATUS_V1, **summary}


@router.get("/v1/runs/{job_id}/events")
def get_run_events(
    job_id: str,
    job_db_path: str | None = Query(default=None, description="Must match enqueue DB"),
) -> dict[str, object]:
    store = sqlite_job_store(job_db_path)
    try:
        tl = store.get_job_timeline_events(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"job not found: {e}") from e
    events_raw = tl.get("events") or []
    events: list[dict[str, object]] = [dict(e) for e in events_raw if isinstance(e, dict)]
    return {
        "schema": JOB_EVENTS_V1,
        "job_id": job_id,
        "note": str(tl.get("source", "")),
        "events": events,
    }


@router.get("/v1/runs/{job_id}/summary")
def get_run_summary_ux(
    job_id: str,
    job_db_path: str | None = Query(default=None, description="Must match enqueue DB"),
) -> dict[str, object]:
    store = sqlite_job_store(job_db_path)
    try:
        row = store.result(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"job not found: {e}") from e
    slim = slim_product_summary_from_pipeline_result(row)
    slim["job_id"] = job_id
    return slim


@router.get("/v1/runs/{job_id}/repro")
def get_run_repro(
    job_id: str,
    job_db_path: str | None = Query(default=None, description="Must match enqueue DB"),
) -> dict[str, object]:
    store = sqlite_job_store(job_db_path)
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
    return {
        "schema": RUN_REPRO_ONLY_V1,
        "job_id": job_id,
        "job_kind": row.get("job_kind"),
        "repro": repro,
    }


@router.get("/v1/runs/{job_id}")
def get_run(
    job_id: str,
    job_db_path: str | None = Query(
        default=None, description="Must match the DB used when enqueueing"
    ),
) -> dict:
    store = sqlite_job_store(job_db_path)
    try:
        return store.result(job_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"job not found: {e}") from e

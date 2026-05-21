from __future__ import annotations

from fastapi import APIRouter

from qchem_stack.api.deps import default_job_db_path, ping_job_db

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def ready() -> dict[str, str]:
    p = default_job_db_path()
    ping_job_db(p)
    return {"status": "ready", "job_db_default": str(p.resolve())}

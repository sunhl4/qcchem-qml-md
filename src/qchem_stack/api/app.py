"""
Minimal HTTP surface for synchronous runs and async SQLite-backed queue.

Bind to ``127.0.0.1`` in production behind a reverse proxy; add authentication
before exposing on a network interface.
"""

from __future__ import annotations

from fastapi import FastAPI

from qchem_stack.api.routers import health, meta, ml_md, runs

app = FastAPI(
    title="qchem-stack",
    version="0.1.0",
    description="Local API + SQLite queue for product workflows and reproducibility metadata.",
    openapi_tags=[
        {"name": "health", "description": "Liveness and readiness probes."},
        {"name": "meta", "description": "Product / parity metadata for dashboards."},
        {
            "name": "product",
            "description": "Workflow stages and computable graph previews for product UX.",
        },
        {
            "name": "ml_md",
            "description": "QMEFDataset validation + MLIP stub hooks (training exports live client-side).",
        },
        {"name": "runs", "description": "Submit experiments and poll SQLite-backed jobs."},
    ],
)

app.include_router(health.router)
app.include_router(meta.router)
app.include_router(ml_md.router)
app.include_router(runs.router)

# Backward-compatible re-exports for tests and integrators.
from qchem_stack.api.deps import (  # noqa: E402
    default_job_db_path,
    experiment_config_from_request_yaml,
)
from qchem_stack.api.models import (  # noqa: E402
    QMEFTrainerStubFitBody,
    QMEFValidateBody,
    RunRequest,
    YamlPreviewBody,
)

__all__ = [
    "app",
    "default_job_db_path",
    "experiment_config_from_request_yaml",
    "RunRequest",
    "YamlPreviewBody",
    "QMEFValidateBody",
    "QMEFTrainerStubFitBody",
]

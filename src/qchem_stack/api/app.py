"""
Minimal HTTP surface for synchronous runs and async SQLite-backed queue.

Bind to ``127.0.0.1`` in production behind a reverse proxy; add authentication
before exposing on a network interface.
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from qchem_stack.api.middleware import AuthenticationMiddleware, limiter
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

# Rate limiting
if limiter is not None:
    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler,  # type: ignore[arg-type]
    )

# CORS middleware — credentials require explicit origins (never ``*`` + credentials).
_cors_origins_raw = os.getenv(
    "QCHEM_STACK_CORS_ORIGINS",
    "http://127.0.0.1:3000,http://127.0.0.1:8000,http://localhost:3000,http://localhost:8000",
)
cors_origins = [origin.strip() for origin in _cors_origins_raw.split(",") if origin.strip()]
_cors_credentials_env = os.getenv("QCHEM_STACK_CORS_CREDENTIALS", "").lower() in {
    "1",
    "true",
    "yes",
}
cors_allow_credentials = _cors_credentials_env and "*" not in cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware (only enabled when API key is configured)
if os.getenv("QCHEM_STACK_API_KEY"):
    app.add_middleware(AuthenticationMiddleware)

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

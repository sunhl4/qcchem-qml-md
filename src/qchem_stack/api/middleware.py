"""API security middleware: authentication and rate limiting."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import Request  # noqa: TC002 — runtime middleware dispatch
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    Limiter = None  # type: ignore[misc, assignment]

_F = TypeVar("_F", bound=Callable[..., Any])

# Shared limiter singleton — routers import this for @limiter.limit decorators.
limiter: Limiter | None = Limiter(key_func=get_remote_address) if SLOWAPI_AVAILABLE else None

# Default route limits (override in tests via monkeypatch if needed).
RUNS_POST_LIMIT = "10/minute"
RUNS_GET_LIMIT = "60/minute"
META_POST_LIMIT = "30/minute"
ML_MD_POST_LIMIT = "30/minute"


def rate_limit(limit: str) -> Callable[[_F], _F]:
    """Apply SlowAPI limit when available; no-op in pytest or when explicitly disabled."""

    def decorator(func: _F) -> _F:
        if os.getenv("QCHEM_STACK_DISABLE_RATE_LIMIT", "").lower() in {"1", "true", "yes"}:
            return func
        if limiter is not None:
            wrapped = limiter.limit(limit)(func)
            return wrapped  # type: ignore[no-any-return]
        return func

    return decorator


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Bearer token authentication middleware.

    Validates Authorization header for Bearer tokens.
    Health endpoints (/health, /health/ready) are excluded from authentication.
    """

    def __init__(self, app: Any, token_validator: Callable[[str], bool] | None = None) -> None:
        super().__init__(app)
        self.token_validator = token_validator or self._default_token_validator

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        if request.url.path in ("/health", "/health/ready"):
            response = await call_next(request)
            return response  # type: ignore[no-any-return]

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(status_code=401, content={"detail": "Missing Authorization header"})

        if not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Invalid Authorization format"})

        token = auth_header[7:]
        if not self.token_validator(token):
            return JSONResponse(status_code=403, content={"detail": "Invalid or expired token"})

        response = await call_next(request)
        return response  # type: ignore[no-any-return]

    @staticmethod
    def _default_token_validator(token: str) -> bool:
        expected = os.environ.get("QCHEM_STACK_API_KEY")
        if not expected:
            return True
        return token == expected


def create_limiter() -> Limiter | None:
    """Return the shared SlowAPI limiter instance (backward-compatible accessor)."""
    return limiter

"""API rate limiting configuration and enforcement tests."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("slowapi")

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from qchem_stack.api.app import app
from qchem_stack.api.middleware import create_limiter, limiter, rate_limit


def test_create_limiter_returns_limiter_instance() -> None:
    assert create_limiter() is limiter
    assert limiter is not None
    assert hasattr(limiter, "limit")


def test_app_has_limiter_when_slowapi_available() -> None:
    assert hasattr(app.state, "limiter")
    assert app.state.limiter is not None


def test_rate_limit_returns_429_after_budget_exhausted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolated app: third request within the window must return 429."""
    monkeypatch.delenv("QCHEM_STACK_DISABLE_RATE_LIMIT", raising=False)
    assert limiter is not None
    test_app = FastAPI()
    test_app.state.limiter = limiter
    test_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @test_app.get("/limited-smoke")
    @rate_limit("2/minute")
    def limited_smoke(request: Request) -> dict[str, str]:
        return {"ok": "true"}

    client = TestClient(test_app)
    assert client.get("/limited-smoke").status_code == 200
    assert client.get("/limited-smoke").status_code == 200
    blocked = client.get("/limited-smoke")
    assert blocked.status_code == 429
    assert "rate limit" in blocked.text.lower() or blocked.status_code == 429


def test_runs_list_route_accepts_request_for_limiter() -> None:
    """list_runs must accept Request (required by SlowAPI limiter wiring)."""
    import inspect

    from qchem_stack.api.routers import runs

    sig = inspect.signature(runs.list_runs)
    assert "request" in sig.parameters

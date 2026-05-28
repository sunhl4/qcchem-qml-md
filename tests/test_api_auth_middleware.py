"""API authentication middleware tests."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi import FastAPI
from fastapi.testclient import TestClient

from qchem_stack.api.middleware import AuthenticationMiddleware


def _app_with_auth() -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/protected")
    def protected() -> dict[str, str]:
        return {"secret": "yes"}

    app.add_middleware(AuthenticationMiddleware)
    return app


def test_health_bypasses_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QCHEM_STACK_API_KEY", "test-key")
    client = TestClient(_app_with_auth())
    r = client.get("/health")
    assert r.status_code == 200


def test_missing_auth_header_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QCHEM_STACK_API_KEY", "test-key")
    client = TestClient(_app_with_auth())
    r = client.get("/protected")
    assert r.status_code == 401


def test_invalid_token_returns_403(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QCHEM_STACK_API_KEY", "correct-key")
    client = TestClient(_app_with_auth())
    r = client.get("/protected", headers={"Authorization": "Bearer wrong-key"})
    assert r.status_code == 403


def test_valid_token_allows_access(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QCHEM_STACK_API_KEY", "correct-key")
    client = TestClient(_app_with_auth())
    r = client.get("/protected", headers={"Authorization": "Bearer correct-key"})
    assert r.status_code == 200
    assert r.json()["secret"] == "yes"

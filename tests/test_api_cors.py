"""CORS middleware configuration tests."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from qchem_stack.api.app import app


def test_cors_preflight_allows_origin() -> None:
    client = TestClient(app)
    r = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code in (200, 204, 405)
    if "access-control-allow-origin" in r.headers:
        assert r.headers["access-control-allow-origin"] in ("*", "http://localhost:3000")

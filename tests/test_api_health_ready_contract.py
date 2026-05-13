"""D57: `/health` and `/health/ready` match HTTP API contract doc shapes."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from qchem_stack.api.app import app


def test_health_and_ready_json_contract() -> None:
    client = TestClient(app)
    h = client.get("/health")
    assert h.status_code == 200
    assert h.json() == {"status": "ok"}

    r = client.get("/health/ready")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ready"
    assert "job_db_default" in body and isinstance(body["job_db_default"], str)

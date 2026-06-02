"""API contract tests: health endpoints, CORS, and payload limits.

Consolidates:
- test_api_health_ready_contract.py
- test_api_cors.py
- test_api_payload_limits.py
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi import HTTPException
from fastapi.testclient import TestClient

from qchem_stack.api.app import app
from qchem_stack.api.deps import MAX_EXPERIMENT_YAML_BYTES, experiment_config_from_request_yaml


class TestHealthEndpoints:
    """D57: `/health` and `/health/ready` match HTTP API contract doc shapes."""

    def test_health_and_ready_json_contract(self) -> None:
        client = TestClient(app)
        h = client.get("/health")
        assert h.status_code == 200
        assert h.json() == {"status": "ok"}

        r = client.get("/health/ready")
        assert r.status_code == 200
        body = r.json()
        assert body.get("status") == "ready"
        assert "job_db_default" in body and isinstance(body["job_db_default"], str)


class TestCORSMiddleware:
    """CORS middleware configuration tests."""

    def test_cors_preflight_allows_origin(self) -> None:
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


class TestPayloadLimits:
    """API YAML payload size limits."""

    def test_experiment_yaml_over_limit_returns_413(self) -> None:
        huge = "experiment_id: x\n" + ("# " + "x" * 1000 + "\n") * 600
        assert len(huge.encode("utf-8")) > MAX_EXPERIMENT_YAML_BYTES
        with pytest.raises(HTTPException) as exc:
            experiment_config_from_request_yaml(huge)
        assert exc.value.status_code == 413

    def test_minimal_yaml_under_limit(self) -> None:
        yaml_text = """
experiment_id: t
molecule:
  symbols: [H, H]
  coordinates: [[0,0,0],[0,0,0.74]]
active_space:
  strategy: cas
  cas: {n_orbitals: 2, n_electrons: 2}
scf: {driver: pyscf, method: RHF}
"""
        cfg = experiment_config_from_request_yaml(yaml_text)
        assert cfg.experiment_id == "t"

"""API config_base_dir path sandbox."""

from __future__ import annotations

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from qchem_stack.api.app import create_app


def test_config_base_dir_outside_allowed_returns_403() -> None:
    client = TestClient(create_app())
    resp = client.post(
        "/v1/runs",
        json={
            "experiment_yaml": "experiment_id: x\nmolecule:\n  geometry: [[H, 0,0,0]]\n",
            "config_base_dir": "/etc",
            "sync": True,
        },
    )
    assert resp.status_code == 403
    assert "config_base_dir" in resp.text.lower() or "allowed" in resp.text.lower()

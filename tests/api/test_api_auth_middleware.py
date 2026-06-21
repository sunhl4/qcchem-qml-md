"""API authentication middleware behavior (reload app when key is configured)."""

from __future__ import annotations

import importlib
import os

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient


def _client_with_api_key(key: str) -> TestClient:
    os.environ["QCHEM_STACK_API_KEY"] = key
    import qchem_stack.api.app as app_mod

    importlib.reload(app_mod)
    return TestClient(app_mod.app)


def test_product_surface_401_without_bearer() -> None:
    client = _client_with_api_key("test-api-key-middleware")
    r = client.get("/v1/meta/product-surface")
    assert r.status_code == 401


def test_product_surface_200_with_valid_bearer() -> None:
    client = _client_with_api_key("test-api-key-middleware")
    r = client.get(
        "/v1/meta/product-surface",
        headers={"Authorization": "Bearer test-api-key-middleware"},
    )
    assert r.status_code == 200
    assert r.json().get("schema") == "product_surface_v1"


def test_health_endpoints_skip_auth() -> None:
    client = _client_with_api_key("test-api-key-middleware")
    assert client.get("/health").status_code == 200
    assert client.get("/health/ready").status_code in {200, 503}

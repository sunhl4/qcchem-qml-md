"""API authentication middleware behavior (reload app when key is configured)."""

from __future__ import annotations

import importlib
import os

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from qchem_stack.exceptions import ConfigurationError


def _reload_app_env(**env: str) -> None:
    for k in (
        "QCHEM_STACK_API_KEY",
        "QCHEM_STACK_REQUIRE_API_KEY",
        "QCHEM_STACK_DISABLE_RATE_LIMIT",
    ):
        os.environ.pop(k, None)
    for k, v in env.items():
        os.environ[k] = v


def _client_with_api_key(key: str) -> TestClient:
    _reload_app_env(QCHEM_STACK_API_KEY=key)
    import qchem_stack.api.app as app_mod

    importlib.reload(app_mod)
    return TestClient(app_mod.app)


@pytest.fixture(autouse=True)
def _cleanup_api_auth_env() -> None:
    """Ensure auth middleware tests do not leak env into other API tests."""
    yield
    for key in ("QCHEM_STACK_API_KEY", "QCHEM_STACK_REQUIRE_API_KEY"):
        os.environ.pop(key, None)


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


def test_require_api_key_without_key_raises_on_import() -> None:
    _reload_app_env(QCHEM_STACK_REQUIRE_API_KEY="1")
    import qchem_stack.api.app as app_mod

    with pytest.raises(ConfigurationError, match="QCHEM_STACK_API_KEY"):
        importlib.reload(app_mod)


def test_require_api_key_with_key_enables_auth() -> None:
    _reload_app_env(
        QCHEM_STACK_API_KEY="prod-key-required",
        QCHEM_STACK_REQUIRE_API_KEY="1",
    )
    import qchem_stack.api.app as app_mod

    importlib.reload(app_mod)
    client = TestClient(app_mod.app)
    assert client.get("/v1/meta/product-surface").status_code == 401
    assert (
        client.get(
            "/v1/meta/product-surface",
            headers={"Authorization": "Bearer prod-key-required"},
        ).status_code
        == 200
    )

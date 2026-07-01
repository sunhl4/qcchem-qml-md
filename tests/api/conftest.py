"""Shared fixtures for API tests."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _open_api_env_for_tests() -> None:
    """Default API tests run without bearer auth unless a test opts in."""
    os.environ.pop("QCHEM_STACK_API_KEY", None)
    os.environ.pop("QCHEM_STACK_REQUIRE_API_KEY", None)
    yield
    os.environ.pop("QCHEM_STACK_API_KEY", None)
    os.environ.pop("QCHEM_STACK_REQUIRE_API_KEY", None)


@pytest.fixture(scope="session")
def _ensure_api_deps() -> None:
    """Skip entire module if FastAPI is not installed."""
    pytest.importorskip("fastapi")


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Authorization headers for authenticated API requests."""
    api_key = os.environ.get("QCHEM_STACK_API_KEY", "test-key-for-pytest")
    return {"Authorization": f"Bearer {api_key}"}


@pytest.fixture
def api_client(_ensure_api_deps: None, tmp_job_db: Path) -> TestClient:
    """FastAPI test client with temporary job database."""
    os.environ["QCHEM_JOB_DB"] = str(tmp_job_db)
    os.environ.pop("QCHEM_STACK_API_KEY", None)
    from fastapi.testclient import TestClient

    from qchem_stack.api.app import create_app

    with TestClient(create_app()) as client:
        yield client

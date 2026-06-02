"""Shared pytest fixtures for qchem-stack tests."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from tests.helpers.h2_yaml import H2_STO3G_FCI_ENERGY, h2_pipeline_dict, h2_yaml_dict
from tests.helpers.solver_registry_state import reset_solver_registry_state

# Full-suite API tests enqueue/list runs frequently; disable route rate limits unless
# a test explicitly opts in (see tests/test_api_rate_limiting.py).
os.environ.setdefault("QCHEM_STACK_DISABLE_RATE_LIMIT", "1")

# P0-2: Set HMAC key for all tests (required by secure_serialization.py)
os.environ.setdefault("QCHEM_PROTOCOL_HMAC_KEY", "test-hmac-key-for-testing-only-32bytes")

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


@pytest.fixture(scope="session")
def pyscf_available() -> bool:
    """True when PySCF imports (session-scoped guard for optional chemistry tests)."""
    try:
        import pyscf  # noqa: F401

        return True
    except ImportError:
        return False


@pytest.fixture(scope="session")
def h2_sto3g_fci_energy() -> float:
    return H2_STO3G_FCI_ENERGY


@pytest.fixture
def h2_yaml_dict_fixture() -> dict[str, Any]:
    return h2_yaml_dict()


@pytest.fixture
def h2_pipeline_dict_fixture() -> dict[str, Any]:
    return h2_pipeline_dict()


@pytest.fixture(autouse=True)
def _isolate_solver_registry_between_tests() -> None:
    """Prevent entrypoint plugin registration from leaking across tests."""
    reset_solver_registry_state()
    yield
    reset_solver_registry_state()


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def h2_config() -> ExperimentConfig:
    """Minimal H2 experiment configuration for testing."""
    from qchem_stack.config import ExperimentConfig

    return ExperimentConfig.model_validate(h2_yaml_dict())


@pytest.fixture
def tmp_job_db(tmp_path: Path) -> Path:
    """Temporary SQLite database for job queue tests."""
    return tmp_path / "test_jobs.sqlite"


@pytest.fixture
def mock_executor():
    """Mock HamiltonianExpectationExecutor for testing."""
    from unittest.mock import MagicMock

    executor = MagicMock()
    executor.expectation_hea.return_value = -1.0
    return executor

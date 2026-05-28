"""Shared pytest fixtures for qchem-stack tests."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

# Full-suite API tests enqueue/list runs frequently; disable route rate limits unless
# a test explicitly opts in (see tests/test_api_rate_limiting.py).
os.environ.setdefault("QCHEM_STACK_DISABLE_RATE_LIMIT", "1")

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Path to test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def h2_config() -> ExperimentConfig:
    """Minimal H2 experiment configuration for testing."""
    from qchem_stack.config import ExperimentConfig

    return ExperimentConfig.model_validate(
        {
            "experiment_id": "test-h2",
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0, 0, 0], [0, 0, 0.74]],
            },
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "scf": {
                "driver": "pyscf",
                "method": "RHF",
            },
        }
    )


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

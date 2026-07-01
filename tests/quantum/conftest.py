"""Shared fixtures for quantum algorithm tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest


@pytest.fixture
def mock_executor() -> MagicMock:
    """Mock HamiltonianExpectationExecutor for testing."""
    executor = MagicMock()
    executor.expectation_hea.return_value = -1.0
    return executor


@pytest.fixture
def sample_angles() -> np.ndarray:
    """Small fixed-angle vector for variational-circuit smoke tests."""
    return np.array([0.1, 0.2, 0.3, 0.4], dtype=float)

"""Backend HEA outputs share numeric contract across providers."""

from __future__ import annotations

import math

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.backends.spec import BackendSpec


def _hea_energy(provider: str) -> float:
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.15) + QubitOperator((), 0.05)
    angles = np.linspace(0.1, 0.8, 8)
    ex = executor_from_spec(BackendSpec(name="contract", provider=provider))
    return float(ex.expectation_hea(h, 2, angles, 2))


def test_statevector_energy_is_finite() -> None:
    e = _hea_energy("statevector")
    assert math.isfinite(e)


@pytest.mark.parametrize("provider", ["qiskit"])
def test_qiskit_mock_matches_statevector_contract(provider: str) -> None:
    pytest.importorskip("qiskit")
    ref = _hea_energy("statevector")
    got = _hea_energy(provider)
    assert got == pytest.approx(ref, rel=1e-4, abs=1e-4)


def test_statevector_executor_returns_float() -> None:
    h = QubitOperator((), 1.0)
    e = StatevectorHeaExecutor().expectation_hea(h, 1, np.zeros(2), 1)
    assert isinstance(e, float)

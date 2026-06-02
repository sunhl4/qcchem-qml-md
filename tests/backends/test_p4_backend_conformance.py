"""Braket/Cirq backend registration and HEA conformance."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.backends.factory import executor_from_spec, registered_backend_provider_ids
from qchem_stack.backends.spec import BackendSpec


@pytest.mark.parametrize("provider", ["statevector", "cirq", "braket"])
def test_multi_backend_hea_conformance(provider: str) -> None:
    if provider == "cirq":
        pytest.importorskip("cirq")
    assert provider in registered_backend_provider_ids()
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.15) + QubitOperator((), 0.05)
    angles = np.linspace(0.1, 0.8, 8)
    ref = StatevectorHeaExecutor().expectation_hea(h, 2, angles, 2)
    ex = executor_from_spec(BackendSpec(name="t", provider=provider))
    got = ex.expectation_hea(h, 2, angles, 2)
    assert got == pytest.approx(ref, rel=1e-4, abs=1e-4)

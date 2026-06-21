"""UQC grouped Pauli vs statevector reference (mock client, no network)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from openfermion.ops import QubitOperator

pytest.importorskip("qiskit")


def test_grouped_uqc_matches_statevector_on_zz_hamiltonian() -> None:
    from qchem_stack.backends.executor_base import StatevectorHeaExecutor
    from qchem_stack.backends.spec import BackendSpec
    from qchem_stack.backends.uqc_executor import UQCCloudHeaExecutor

    h = QubitOperator("Z0", 0.5) + QubitOperator("Z1", 0.3) + QubitOperator("", -0.8)
    nq = 2
    depth = 1
    angles = np.array([0.2, -0.1, 0.05, 0.15], dtype=float)
    ref = StatevectorHeaExecutor().expectation_hea(h, nq, angles, depth)

    mock_client = MagicMock()
    mock_client.submit_task.return_value = "t1"
    mock_client.get_task_status.return_value = "SUCCESS"
    # |00⟩ dominant → Z0,Z1 eigenvalues +1
    mock_client.get_task_result.return_value = [
        {"datasets": {"computational_basis_histogram": [[0, 100]]}}
    ]

    spec = BackendSpec(
        name="uqc-grouped",
        provider="uqc",
        shots_per_circuit=500,
        meta={
            "uqc_token": "x",
            "uqc_target": "iontrap-sim",
            "uqc_multi_basis_pauli": True,
        },
    )
    ex = UQCCloudHeaExecutor(spec)
    ex._client = mock_client

    with patch("uqc_client.ensure_static_qasm"):
        got = ex._execute_on_uqc(h, nq, angles, depth)

    assert got == pytest.approx(ref, abs=0.15)
    assert mock_client.submit_task.call_count >= 1


def test_mock_mode_uses_statevector_not_cloud() -> None:
    from qchem_stack.backends.spec import BackendSpec
    from qchem_stack.backends.uqc_executor import UQCCloudHeaExecutor

    spec = BackendSpec(name="uqc-mock", provider="uqc", shots_per_circuit=100, uqc_mode="mock")
    ex = UQCCloudHeaExecutor(spec)
    h = QubitOperator("Z0", 1.0)
    e = ex.expectation_hea(h, 1, np.zeros(2), 1)
    assert isinstance(e, float)

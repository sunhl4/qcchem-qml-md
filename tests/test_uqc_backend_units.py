"""Unit tests for UQC backend helpers (no real hardware)."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from openfermion.ops import QubitOperator

pytest.importorskip("qiskit")


def test_load_repo_dotenv_sets_missing_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from qchem_stack.backends import uqc_env

    env_file = tmp_path / ".env"
    env_file.write_text("UQC_TEST_KEY=from_file\nEXISTING=from_file\n", encoding="utf-8")
    monkeypatch.setenv("EXISTING", "already_set")
    monkeypatch.delenv("UQC_TEST_KEY", raising=False)

    with patch.object(uqc_env, "_REPO_ROOT", tmp_path):
        uqc_env.load_repo_dotenv()

    assert os.environ["UQC_TEST_KEY"] == "from_file"
    assert os.environ["EXISTING"] == "already_set"


def test_uqc_transpiler_native_gates_and_qasm3() -> None:
    from qiskit import QuantumCircuit

    from qchem_stack.backends.uqc_transpiler import (
        circuit_to_qasm3_uqc,
        transpile_to_uqc_native,
        validate_uqc_circuit,
    )

    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    transpiled = transpile_to_uqc_native(qc, optimization_level=1)
    assert validate_uqc_circuit(transpiled)
    qasm = circuit_to_qasm3_uqc(transpiled)
    assert "OPENQASM" in qasm or "qubit" in qasm.lower()

    bad = QuantumCircuit(1)
    bad.h(0)
    with pytest.raises(ValueError, match="not supported by UQC"):
        circuit_to_qasm3_uqc(bad)


def test_uqc_pauli_measurement_parity_and_expectation() -> None:
    from qchem_stack.backends.uqc_pauli_measurement import (
        _bitstring_to_parity,
        _evaluate_pauli_term_from_counts,
        compute_hamiltonian_expectation_from_counts,
    )

    assert _bitstring_to_parity("0", [0]) == 1
    assert _bitstring_to_parity("1", [0]) == -1

    counts = {"00": 50, "11": 50}
    z0 = _evaluate_pauli_term_from_counts(counts, [0], 2)
    assert z0 == pytest.approx(0.0)

    counts_z1 = {"00": 100}
    assert _evaluate_pauli_term_from_counts(counts_z1, [1], 2) == pytest.approx(1.0)

    h = QubitOperator("Z0", 1.0) + QubitOperator("", 0.5)
    exp = compute_hamiltonian_expectation_from_counts(counts, h, 2)
    assert exp == pytest.approx(0.5)

    assert compute_hamiltonian_expectation_from_counts({}, h, 2) == pytest.approx(0.5)


def test_uqc_executor_mock_mode() -> None:
    from qchem_stack.backends.spec import BackendSpec
    from qchem_stack.backends.uqc_executor import UQCCloudHeaExecutor

    spec = BackendSpec(name="uqc-mock", provider="uqc", shots_per_circuit=100, uqc_mode="mock")
    ex = UQCCloudHeaExecutor(spec)
    h = QubitOperator("Z0", 1.0)
    angles = np.zeros(2)
    e = ex.expectation_hea(h, 1, angles, 1)
    assert isinstance(e, float)


def test_uqc_executor_injected_expectation_fn() -> None:
    from qchem_stack.backends.spec import BackendSpec
    from qchem_stack.backends.uqc_executor import UQCCloudHeaExecutor

    def _fn(h, n, angles, depth):
        return 42.0

    spec = BackendSpec(
        name="uqc-inject",
        provider="uqc",
        shots_per_circuit=100,
        meta={"expectation_fn": _fn},
    )
    ex = UQCCloudHeaExecutor(spec)
    h = QubitOperator("Z0", 1.0)
    assert ex.expectation_hea(h, 1, np.zeros(4), 1) == 42.0


def test_uqc_executor_client_requires_token() -> None:
    from qchem_stack.backends.spec import BackendSpec
    from qchem_stack.backends.uqc_executor import UQCCloudHeaExecutor

    spec = BackendSpec(name="uqc-no-token", provider="uqc", shots_per_circuit=100)
    ex = UQCCloudHeaExecutor(spec)
    with (
        patch.dict(os.environ, {}, clear=True),
        patch("qchem_stack.backends.uqc_env.load_repo_dotenv"),
        pytest.raises(ValueError, match="UQC API token"),
    ):
        ex._client = None
        ex._get_uqc_client()


def test_uqc_executor_artiq_histogram_to_counts() -> None:
    from qchem_stack.backends.uqc_executor import UQCCloudHeaExecutor

    counts = UQCCloudHeaExecutor._artiq_histogram_to_counts([[0, 10], [3, 5]], 2)
    assert counts == {"00": 10, "11": 5}


def test_uqc_executor_cloud_path_with_mock_client() -> None:
    pytest.importorskip("qiskit")
    from qchem_stack.backends.spec import BackendSpec
    from qchem_stack.backends.uqc_executor import UQCCloudHeaExecutor

    mock_client = MagicMock()
    mock_client.submit_task.return_value = "task-1"
    mock_client.get_task_status.return_value = "SUCCESS"
    mock_client.get_task_result.return_value = [
        {"datasets": {"computational_basis_histogram": [[0, 100]]}}
    ]

    spec = BackendSpec(
        name="uqc-cloud",
        provider="uqc",
        shots_per_circuit=200,
        meta={"uqc_token": "test-token", "uqc_target": "iontrap-sim"},
    )
    ex = UQCCloudHeaExecutor(spec)
    ex._client = mock_client

    h = QubitOperator("Z0", 1.0)
    angles = np.array([0.1, 0.2])
    with patch("uqc_client.ensure_static_qasm"):
        e = ex._execute_on_uqc(h, 1, angles, 1)
    assert isinstance(e, float)
    mock_client.submit_task.assert_called_once()


def test_uqc_executor_cloud_failure_no_fallback() -> None:
    from qchem_stack.backends.spec import BackendSpec
    from qchem_stack.backends.uqc_executor import UQCCloudHeaExecutor

    mock_client = MagicMock()
    mock_client.submit_task.side_effect = RuntimeError("network down")

    spec = BackendSpec(
        name="uqc-no-fallback",
        provider="uqc",
        shots_per_circuit=200,
        meta={"uqc_token": "test-token", "uqc_allow_fallback": False},
    )
    ex = UQCCloudHeaExecutor(spec)
    ex._client = mock_client

    h = QubitOperator("Z0", 1.0)
    with (
        patch("uqc_client.ensure_static_qasm"),
        pytest.raises(RuntimeError, match="uqc_allow_fallback=false"),
    ):
        ex._execute_on_uqc(h, 1, np.array([0.1, 0.2]), 1)

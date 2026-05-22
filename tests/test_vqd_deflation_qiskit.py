"""VQD deflation swap-test Qiskit export."""

from __future__ import annotations

import pytest

pytest.importorskip("qiskit")

from qchem_stack.backends.vqd_deflation_qiskit import (
    deflation_swap_test_circuit_ir,
    deflation_swap_test_qiskit_export_v1,
)


def test_deflation_swap_test_qiskit_export_h2_active_space() -> None:
    ir = deflation_swap_test_circuit_ir(n_system_qubits=2)
    assert ir.n_qubits == 5
    assert any(str(op.get("name")) == "CSWAP" for op in ir.operations)
    export = deflation_swap_test_qiskit_export_v1(n_system_qubits=2)
    assert export["schema"] == "vqd_deflation_swap_test_qiskit_export_v1"
    assert export["n_qubits"] == 5
    assert export["twoq_gate_count"] >= 2
    assert export["depth_estimate"] >= 1

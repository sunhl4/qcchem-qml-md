"""Qiskit export for VQD deflation swap-test CircuitIR sketches."""

from __future__ import annotations

from typing import Any, cast

from qchem_stack.backends.spec import CircuitIR
from qchem_stack.quantum.algorithms.excited_basis import vqd_deflation_swap_test_circuit_sketch


def deflation_swap_test_circuit_ir(*, n_system_qubits: int) -> CircuitIR:
    sketch = vqd_deflation_swap_test_circuit_sketch(n_system_qubits=int(n_system_qubits))
    return CircuitIR(
        n_qubits=int(sketch["n_qubits"]),
        operations=cast("list[dict[str, Any]]", list(sketch["operations"])),
        boxes=list(sketch.get("boxes") or []),
    )


def deflation_swap_test_qiskit_export_v1(*, n_system_qubits: int) -> dict[str, Any]:
    """Build Qiskit circuit + resource summary for parity / Methods export."""
    from qchem_stack.backends.uccsd_circuit_qiskit import circuit_ir_to_qiskit

    ir = deflation_swap_test_circuit_ir(n_system_qubits=n_system_qubits)
    qc = circuit_ir_to_qiskit(ir)
    n_2q = sum(1 for ins in qc.data if len(ins.qubits) >= 2)
    return {
        "schema": "vqd_deflation_swap_test_qiskit_export_v1",
        "n_system_qubits": int(n_system_qubits),
        "n_qubits": int(ir.n_qubits),
        "depth_estimate": int(qc.depth()),
        "twoq_gate_count": int(n_2q),
        "operation_count": len(qc.data),
        "qiskit_circuit_name": getattr(qc, "name", None) or "vqd_deflation_swap_test",
    }

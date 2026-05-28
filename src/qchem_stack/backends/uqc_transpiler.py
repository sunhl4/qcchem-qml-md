"""
Transpile Qiskit circuits to UQC ion-trap native gate set (rzz, rx, ry).

UQC ion-trap quantum computers support only rzz, rx, ry as basic gates.
This module provides transpilation utilities to convert arbitrary Qiskit
circuits to this native gate set.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qiskit import QuantumCircuit


def transpile_to_uqc_native(qc: QuantumCircuit, optimization_level: int = 2) -> QuantumCircuit:
    """Transpile a Qiskit circuit to UQC native gates (rzz, rx, ry).

    Args:
        qc: Input Qiskit QuantumCircuit.
        optimization_level: Qiskit transpiler optimization level (0-3).

    Returns:
        Transpiled QuantumCircuit using only rzz, rx, ry gates.
    """
    from qiskit import transpile

    basis_gates = ["rzz", "rx", "ry"]

    transpiled = transpile(
        qc,
        basis_gates=basis_gates,
        optimization_level=optimization_level,
    )

    return transpiled


def validate_uqc_circuit(qc: QuantumCircuit) -> bool:
    """Check if a circuit uses only UQC native gates.

    Args:
        qc: Qiskit QuantumCircuit to validate.

    Returns:
        True if circuit uses only rzz, rx, ry gates.
    """
    native_gates = {"rzz", "rx", "ry", "barrier", "measure"}

    for instruction in qc.data:
        gate_name = instruction.operation.name.lower()
        if gate_name not in native_gates:
            return False
    return True


def circuit_to_qasm3_uqc(qc: QuantumCircuit) -> str:
    """Export a transpiled circuit to OpenQASM 3.0 format for UQC submission.

    Uses ``qiskit.qasm3.dumps()`` (the canonical Qiskit 2.x API) rather than
    ``qc.qasm3()`` which may produce slightly different output.

    Args:
        qc: Transpiled Qiskit QuantumCircuit (must use only rzz, rx, ry).

    Returns:
        OpenQASM 3.0 string representation.

    Raises:
        ValueError: If circuit contains unsupported gates.
    """
    if not validate_uqc_circuit(qc):
        raise ValueError(
            "Circuit contains gates not supported by UQC. "
            "Transpile using transpile_to_uqc_native() first."
        )

    from qiskit.qasm3 import dumps

    return dumps(qc)

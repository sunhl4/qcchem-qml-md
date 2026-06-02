"""Cirq HEA expectation executor with OpenFermion qubit indexing.

**Qubit Index Convention**:
OpenFermion uses tensor-product ordering where qubit index ``q`` corresponds to tensor axis ``q``.
Cirq uses big-endian convention where qubit 0 is the most significant bit (leftmost),
which matches OpenFermion's ordering. This executor uses direct qubit indexing without reversal.

The mapping is applied in:
- :func:`_hea_circuit_cirq`: rotation and CNOT gates use ``LineQubit(q)`` directly
- :func:`_pauli_expectation_cirq`: Pauli operators use ``qubits[int(idx)]`` directly

This ensures that expectation values match the NumPy reference within numerical precision.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.spec import BackendSpec

logger = logging.getLogger(__name__)


def _hea_circuit_cirq(n_qubits: int, depth: int, angles: np.ndarray) -> Any:
    """Build HEA circuit in Cirq matching OpenFermion qubit ordering.

    Returns ``(circuit, qubits)`` tuple.
    """
    import cirq

    qubits = [cirq.LineQubit(i) for i in range(n_qubits)]
    circuit = cirq.Circuit()
    k = 0
    for _ in range(depth):
        for q in range(n_qubits):
            circuit.append(cirq.ry(float(angles[k])).on(qubits[q]))
            k += 1
            circuit.append(cirq.rx(float(angles[k])).on(qubits[q]))
            k += 1
        for q in range(n_qubits - 1):
            circuit.append(cirq.CNOT(qubits[q], qubits[q + 1]))
    return circuit, qubits


def _pauli_expectation_cirq(
    circuit: Any, qubits: list[Any], hamiltonian: QubitOperator, n_qubits: int
) -> float:
    """Compute ``<H>`` via Cirq ``Simulator`` with exact statevector expectation values."""
    import cirq

    sim = cirq.Simulator()
    result = sim.simulate(circuit, initial_state=0)

    total = 0.0
    for term, coeff in hamiltonian.terms.items():
        c = float(np.real(coeff))
        if not term:
            total += c
            continue
        obs_ops: list[Any] = []
        for idx, pauli in sorted(term, key=lambda x: x[0]):
            if pauli == "X":
                obs_ops.append(cirq.X(qubits[int(idx)]))
            elif pauli == "Y":
                obs_ops.append(cirq.Y(qubits[int(idx)]))
            elif pauli == "Z":
                obs_ops.append(cirq.Z(qubits[int(idx)]))
        if not obs_ops:
            continue
        op = obs_ops[0] if len(obs_ops) == 1 else cirq.PauliString(obs_ops)
        exp = float(result.expectation_values([op])[0])
        total += c * exp
    return float(total)


class CirqHeaExecutor:
    """Cirq ``Simulator`` HEA Hamiltonian expectation.

    Uses the native Cirq simulator when available; falls back to the reference
    NumPy ``StatevectorHeaExecutor`` when Cirq is not installed.
    """

    def __init__(self, spec: BackendSpec | None = None) -> None:
        self.spec = spec

    def expectation_hea(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        try:
            import cirq  # noqa: F401
        except ImportError:
            logger.debug("Cirq not available, falling back to statevector executor")
            from qchem_stack.backends.executor_base import StatevectorHeaExecutor

            return StatevectorHeaExecutor().expectation_hea(
                hamiltonian, n_qubits, angles, hea_depth
            )

        circuit, qubits = _hea_circuit_cirq(n_qubits, hea_depth, np.asarray(angles, dtype=float))
        return _pauli_expectation_cirq(circuit, qubits, hamiltonian, n_qubits)

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        return StatevectorHeaExecutor().expectation_state(state, hamiltonian, n_qubits)

"""Cirq HEA expectation executor (OpenFermion qubit indexing)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.spec import BackendSpec


def _hea_circuit_cirq(n_qubits: int, depth: int, angles: np.ndarray) -> Any:
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
    import cirq

    total = 0.0
    for term, coeff in hamiltonian.terms.items():
        c = float(np.real(coeff))
        if not term:
            total += c
            continue
        meas = cirq.Circuit(circuit)
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
        sim = cirq.Simulator()
        result = sim.simulate(meas, initial_state=0)
        exp = float(result.expectation_values([op])[0])
        total += c * exp
    return float(total)


class CirqHeaExecutor:
    """Cirq ``Simulator`` HEA Hamiltonian expectation."""

    def __init__(self, spec: BackendSpec | None = None) -> None:
        self.spec = spec

    def expectation_hea(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        return StatevectorHeaExecutor().expectation_hea(hamiltonian, n_qubits, angles, hea_depth)

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        return StatevectorHeaExecutor().expectation_state(state, hamiltonian, n_qubits)

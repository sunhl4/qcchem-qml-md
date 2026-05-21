from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.spec import BackendSpec


def openfermion_to_sparse_pauli_op(qop: QubitOperator, n_qubits: int) -> Any:
    """OpenFermion index ``i`` (tensor axis ``i``) → Qiskit Pauli string, MSB-first (left) = wire ``n-1``."""
    from qiskit.quantum_info import SparsePauliOp

    labels: list[tuple[str, complex]] = []
    for term, coeff in qop.terms.items():
        chars = ["I"] * n_qubits
        for idx, p in term:
            if idx < 0 or idx >= n_qubits:
                raise ValueError(f"Pauli index {idx} out of range for n_qubits={n_qubits}")
            chars[idx] = p
        label = "".join(chars)
        labels.append((label, complex(coeff)))
    if not labels:
        return SparsePauliOp.from_list([("I" * n_qubits, 0.0)])
    return SparsePauliOp.from_list(labels)


def hea_circuit_qiskit(n_qubits: int, depth: int, angles: np.ndarray) -> Any:
    """Match ``hea_state`` tensor axes: logical qubit ``q`` (axis ``q``) maps to wire ``n-1-q`` (Qiskit q0 = LSB)."""
    from qiskit import QuantumCircuit

    def w(q: int) -> int:
        return n_qubits - 1 - q

    n_params = 2 * n_qubits * depth
    if angles.size != n_params:
        raise ValueError(f"expected {n_params} angles, got {angles.size}")
    qc = QuantumCircuit(n_qubits)
    k = 0
    for _ in range(depth):
        for q in range(n_qubits):
            qc.ry(float(angles[k]), w(q))
            k += 1
            qc.rx(float(angles[k]), w(q))
            k += 1
        for q in range(n_qubits - 1):
            qc.cx(w(q), w(q + 1))
    return qc


class QiskitStatevectorHeaExecutor:
    """Qiskit ``Statevector`` expectation (exact, no shots)."""

    def __init__(self, spec: BackendSpec | None = None) -> None:
        self.spec = spec

    def expectation_hea(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        from qiskit.quantum_info import Statevector

        qc = hea_circuit_qiskit(n_qubits, hea_depth, np.asarray(angles, dtype=float))
        sv = Statevector.from_instruction(qc)
        return self.expectation_state(np.array(sv.data), hamiltonian, n_qubits)

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        from qiskit.quantum_info import Statevector

        sv = Statevector(state)
        op = openfermion_to_sparse_pauli_op(hamiltonian, n_qubits)
        exp = sv.expectation_value(op)
        return float(np.real(exp))


class QiskitPrimitivesHeaExecutor:
    """``StatevectorEstimator`` / ``Estimator`` fallback for Qiskit 1.x."""

    def __init__(self, spec: BackendSpec) -> None:
        self.spec = spec

    def expectation_hea(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        qc = hea_circuit_qiskit(n_qubits, hea_depth, np.asarray(angles, dtype=float))
        op = openfermion_to_sparse_pauli_op(hamiltonian, n_qubits)

        try:
            from qiskit.primitives import StatevectorEstimator

            est = StatevectorEstimator()
            job = est.run([(qc, op)])
            pub = job.result()[0]
            ev = getattr(pub.data, "evs", None)
            if ev is not None:
                return float(np.real(ev))
            return float(np.real(np.asarray(pub.data.evs)))  # type: ignore[attr-defined]
        except Exception:
            pass

        from qiskit.primitives import Estimator  # type: ignore[attr-defined]

        est = Estimator(options={"default_shots": int(self.spec.shots_per_circuit)})
        job = est.run([qc], [op])
        res = job.result()
        return float(np.real(res.values[0]))

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        """Shot/primitive path does not accept arbitrary circuits; use statevector math."""
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        return StatevectorHeaExecutor().expectation_state(state, hamiltonian, n_qubits)

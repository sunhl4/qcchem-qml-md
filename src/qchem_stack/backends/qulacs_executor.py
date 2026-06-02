"""Qulacs HEA executor with OpenFermion qubit ordering.

**Qubit Index Convention**:
OpenFermion uses tensor-product ordering where qubit index ``q`` corresponds to tensor axis ``q``.
Qulacs uses little-endian convention where qubit 0 is the least significant bit (rightmost),
similar to Qiskit. This executor maps OpenFermion qubit ``q`` to Qulacs wire ``n_qubits - 1 - q``
to maintain consistency with the statevector reference implementation.

The mapping is applied in:
- :func:`hea_circuit_qulacs`: rotation and CNOT gates use ``w(q) = n_qubits - 1 - q``
- :func:`_openfermion_to_qulacs_observable`: Pauli operators use ``wire(idx) = n_qubits - 1 - idx``

Note: The executor builds circuits using the NumPy statevector reference (:func:`hea_state`)
and loads the result into Qulacs, bypassing the native Qulacs circuit builder for consistency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.spec import BackendSpec


def _openfermion_to_qulacs_observable(hamiltonian: QubitOperator, n_qubits: int) -> Any:
    from qulacs import Observable

    obs = Observable(n_qubits)

    def wire(idx: int) -> int:
        return n_qubits - 1 - int(idx)

    for term, coeff in hamiltonian.terms.items():
        c = float(np.real(coeff))
        if not term:
            obs.add_operator(c, "")
            continue
        pauli = " ".join(f"{p} {wire(idx)}" for idx, p in sorted(term, key=lambda x: x[0]))
        obs.add_operator(c, pauli)
    return obs


def hea_circuit_qulacs(n_qubits: int, depth: int, angles: np.ndarray) -> Any:
    """HEA on Qulacs wires with OpenFermion index ``q`` mapped to wire ``n-1-q`` (Qiskit-style)."""
    from qulacs import QuantumCircuit

    def w(q: int) -> int:
        return n_qubits - 1 - q

    n_params = 2 * n_qubits * depth
    if angles.size != n_params:
        raise ValueError(f"expected {n_params} angles, got {angles.size}")
    qc = QuantumCircuit(n_qubits)
    k = 0
    for _ in range(depth):
        for q in range(n_qubits):
            qc.add_RY_gate(w(q), float(angles[k]))
            k += 1
            qc.add_RX_gate(w(q), float(angles[k]))
            k += 1
        for q in range(n_qubits - 1):
            qc.add_CNOT_gate(w(q), w(q + 1))
    return qc


class QulacsHeaExecutor:
    """Qulacs ``QuantumState`` + ``Observable`` HEA expectation (OpenFermion indexing)."""

    def __init__(self, spec: BackendSpec | None = None) -> None:
        self.spec = spec

    def expectation_hea(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        from qulacs import QuantumState

        from qchem_stack.quantum.statevector import hea_state

        st = hea_state(np.asarray(angles, dtype=float), n_qubits, hea_depth)
        qs = QuantumState(n_qubits)
        qs.load(st.tolist())
        obs = _openfermion_to_qulacs_observable(hamiltonian, n_qubits)
        return float(obs.get_expectation_value(qs))

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        from qulacs import QuantumState

        qs = QuantumState(n_qubits)
        qs.load(np.asarray(state, dtype=complex).reshape(-1).tolist())
        obs = _openfermion_to_qulacs_observable(hamiltonian, n_qubits)
        return float(obs.get_expectation_value(qs))

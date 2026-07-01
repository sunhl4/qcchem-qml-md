"""Amazon Braket local-simulator HEA executor (optional dependency).

**Qubit Index Convention**:
OpenFermion uses tensor-product ordering where qubit index ``q`` corresponds to tensor axis ``q``.
Amazon Braket uses big-endian convention where qubit 0 is the most significant bit (leftmost),
which matches OpenFermion's ordering. This executor uses direct qubit indexing without reversal.

The mapping is applied in:
- :func:`_hea_circuit_braket`: rotation and CNOT gates use direct qubit index ``q``
- Expectation values are computed via statevector using :func:`expectation_qubit_operator`

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


def _hea_circuit_braket(n_qubits: int, depth: int, angles: np.ndarray) -> Any:
    """Build HEA circuit in Braket matching OpenFermion qubit ordering."""
    from braket.circuits import Circuit

    circuit = Circuit()
    k = 0
    for _ in range(depth):
        for q in range(n_qubits):
            circuit.ry(q, float(angles[k]))
            k += 1
            circuit.rx(q, float(angles[k]))
            k += 1
        for q in range(n_qubits - 1):
            circuit.cnot(q, q + 1)
    return circuit


def _pauli_expectation_braket(circuit: Any, hamiltonian: QubitOperator, n_qubits: int) -> float:
    """Compute ``<H>`` via Braket ``LocalSimulator`` statevector + manual Pauli expectation."""
    import contextlib

    from braket.devices import LocalSimulator

    # Newer amazon-braket-sdk refuses ``run(circuit, shots=0)`` unless the circuit
    # declares an explicit result type. Attach a state-vector result type so the
    # simulator returns the wavefunction we consume below. Older SDKs already
    # inject a result type, so the call is a no-op there.
    with contextlib.suppress(
        Exception
    ):  # pragma: no cover - older SDKs already inject a result type
        circuit.state_vector()

    sim = LocalSimulator()
    task = sim.run(circuit, shots=0)
    sv = np.asarray(task.result().values[0], dtype=complex)

    from qchem_stack.quantum.statevector import expectation_qubit_operator

    return float(np.real(expectation_qubit_operator(sv, hamiltonian, n_qubits)))


class BraketHeaExecutor:
    """Braket ``LocalSimulator`` adapter; falls back to statevector when Braket missing.

    Uses the native Braket local simulator when available; falls back to the
    reference NumPy ``StatevectorHeaExecutor`` when amazon-braket-sdk is not installed.
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
            from braket.circuits import Circuit  # noqa: F401
            from braket.devices import LocalSimulator  # noqa: F401
        except ImportError:
            logger.debug("Braket not available, falling back to statevector executor")
            from qchem_stack.backends.executor_base import StatevectorHeaExecutor

            return StatevectorHeaExecutor().expectation_hea(
                hamiltonian, n_qubits, angles, hea_depth
            )

        circuit = _hea_circuit_braket(n_qubits, hea_depth, np.asarray(angles, dtype=float))
        return _pauli_expectation_braket(circuit, hamiltonian, n_qubits)

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        return StatevectorHeaExecutor().expectation_state(state, hamiltonian, n_qubits)

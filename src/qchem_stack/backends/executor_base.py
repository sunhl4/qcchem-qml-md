from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

import numpy as np

from qchem_stack.quantum.statevector import expectation_qubit_operator, hea_state

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

# Hardware note: grouped Pauli readouts can populate
# ``PauliAveragingProtocol._counts["measurement_histogram_rows"]`` directly from device
# job results (same schema as ``pauli_shot_sim``). No extra executor method is required
# if the orchestration layer maps bitstrings to that structure.


@runtime_checkable
class HamiltonianExpectationExecutor(Protocol):
    """Simulator/device API: HEA energy and optional expectation on an explicit statevector."""

    def expectation_hea(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float: ...

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        """``<psi|H|psi>`` for normalized complex ``state`` (length ``2**n_qubits``)."""
        ...


class StatevectorHeaExecutor:
    """Reference: NumPy statevector (OpenFermion Pauli indexing)."""

    def expectation_hea(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        st = hea_state(angles, n_qubits, hea_depth)
        return self.expectation_state(st, hamiltonian, n_qubits)

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        return float(np.real(expectation_qubit_operator(state, hamiltonian, n_qubits)))

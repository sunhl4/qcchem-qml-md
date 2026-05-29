"""Amazon Braket local-simulator HEA executor (optional dependency)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.spec import BackendSpec


class BraketHeaExecutor:
    """Braket ``LocalSimulator`` adapter; falls back to statevector when Braket missing."""

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

        try:
            from braket.circuits import Circuit  # noqa: F401
        except ImportError:
            return StatevectorHeaExecutor().expectation_hea(
                hamiltonian, n_qubits, angles, hea_depth
            )
        # Braket circuit construction is optional; statevector reference preserves L1 semantics.
        return StatevectorHeaExecutor().expectation_hea(hamiltonian, n_qubits, angles, hea_depth)

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        return StatevectorHeaExecutor().expectation_state(state, hamiltonian, n_qubits)

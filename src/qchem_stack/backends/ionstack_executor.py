from __future__ import annotations

from typing import Callable

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec

ExpectationFn = Callable[[QubitOperator, int, np.ndarray, int], float]
ExpectationStateFn = Callable[[np.ndarray, QubitOperator, int], float]


class IonStackHeaExecutor:
    """Placeholder for company IonStack: inject ``meta['expectation_fn']`` or extend with REST/gRPC client."""

    def __init__(self, spec: BackendSpec) -> None:
        self.spec = spec

    def expectation_hea(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        meta = self.spec.meta or {}
        fn: ExpectationFn | None = meta.get("expectation_fn")
        if fn is not None:
            return float(fn(hamiltonian, n_qubits, angles, hea_depth))
        endpoint = meta.get("ionstack_endpoint") or self.spec.ionstack_endpoint
        if endpoint == "mock" and meta.get("mock_energy") is not None:
            return float(meta["mock_energy"])
        raise NotImplementedError(
            "IonStack executor: set backend.meta['expectation_fn'] or implement client for "
            f"endpoint={endpoint!r}. See qchem_stack.backends.ionstack_executor.IonStackHeaExecutor."
        )

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        meta = self.spec.meta or {}
        fn: ExpectationStateFn | None = meta.get("expectation_state_fn")
        if fn is not None:
            return float(fn(state, hamiltonian, n_qubits))
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        return StatevectorHeaExecutor().expectation_state(state, hamiltonian, n_qubits)

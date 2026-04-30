from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.optimize import minimize

from qchem_stack.chem.hamiltonian import QubitHamiltonian

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


@dataclass
class VQEResult:
    energy: float
    angles: np.ndarray
    nfev: int
    meta: dict[str, Any] = field(default_factory=dict)


class VQE:
    """Variational quantum eigensolver; energy via :class:`HamiltonianExpectationExecutor` (Qiskit / IonStack / NumPy)."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        depth: int = 1,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        self.hamiltonian = hamiltonian
        self.depth = depth
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self.n_params = 2 * self.n_qubits * depth
        self._executor = executor or StatevectorHeaExecutor()

    def run(
        self,
        maxiter: int = 200,
        initial_parameters: np.ndarray | None = None,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> VQEResult:
        exe = executor or self._executor
        rng = np.random.default_rng(seed)
        x0 = (
            initial_parameters
            if initial_parameters is not None
            else rng.uniform(-np.pi, np.pi, size=self.n_params)
        )
        nfev = 0

        def objective(x: np.ndarray) -> float:
            nonlocal nfev
            nfev += 1
            return exe.expectation_hea(self.h_op, self.n_qubits, x, self.depth)

        res = minimize(objective, x0, method="COBYLA", options={"maxiter": maxiter})
        return VQEResult(
            energy=float(res.fun),
            angles=np.asarray(res.x),
            nfev=nfev,
            meta={"scipy_message": str(res.message)},
        )

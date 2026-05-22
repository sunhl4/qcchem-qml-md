"""State-averaged VQE (minimal SA-VQE) with overlap penalty to low excited manifolds."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.optimize import minimize

from qchem_stack.quantum.statevector import hea_state

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class SAVQEResult:
    energy: float
    angles: np.ndarray
    nfev: int
    meta: dict[str, Any] = field(default_factory=dict)


class SAVQE:
    """Minimal SA-VQE: optimize ``E + w * overlap^2`` against a reference HEA state."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        *,
        depth: int = 1,
        penalty_weight: float = 2.0,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        self.hamiltonian = hamiltonian
        self.depth = int(depth)
        self.penalty_weight = float(penalty_weight)
        self._executor = executor or StatevectorHeaExecutor()

    def run(
        self,
        *,
        reference_angles: np.ndarray | None = None,
        maxiter: int = 200,
        seed: int = 0,
    ) -> SAVQEResult:
        rng = np.random.default_rng(seed)
        n_q = self.hamiltonian.n_qubits
        n_param = 2 * n_q * self.depth
        ref = (
            np.asarray(reference_angles, dtype=float).ravel()
            if reference_angles is not None
            else rng.uniform(-0.2, 0.2, n_param)
        )
        psi_ref = hea_state(ref, n_q, self.depth)
        exe = self._executor
        h = self.hamiltonian.operator

        def objective(x: np.ndarray) -> float:
            psi = hea_state(np.asarray(x, dtype=float), n_q, self.depth)
            e = float(np.real(exe.expectation_state(psi, h, n_q)))
            ov = float(abs(np.vdot(psi_ref, psi)) ** 2)
            return e + self.penalty_weight * ov

        x0 = rng.uniform(-0.1, 0.1, n_param)
        r = minimize(objective, x0, method="COBYLA", options={"maxiter": int(maxiter)})
        psi = hea_state(np.asarray(r.x, dtype=float), n_q, self.depth)
        e = float(np.real(exe.expectation_state(psi, h, n_q)))
        return SAVQEResult(
            energy=e,
            angles=np.asarray(r.x, dtype=float),
            nfev=int(getattr(r, "nfev", 0) or 0),
            meta={
                "algorithm": "sa_vqe",
                "penalty_weight": self.penalty_weight,
                "reference_overlap_squared": float(abs(np.vdot(psi_ref, psi)) ** 2),
            },
        )

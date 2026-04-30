from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.optimize import minimize

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.statevector import apply_excitation_simple, hea_state

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


@dataclass
class AdaptResult:
    energy: float
    pool_indices: list[tuple[int, int]]
    angles_per_layer: list[float]
    meta: dict[str, Any] = field(default_factory=dict)


class FermionicAdaptVQE:
    """Greedy ADAPT-like loop using a toy qubit pool ``(i,j) -> exp(i*theta X_i X_j)``."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        pool: list[tuple[int, int]] | None = None,
        max_ops: int = 4,
        hea_depth: int = 1,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        self.hamiltonian = hamiltonian
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self.max_ops = max_ops
        self.hea_depth = hea_depth
        self._executor = executor or StatevectorHeaExecutor()
        if pool is None:
            self.pool = [(i, j) for i in range(self.n_qubits) for j in range(i + 1, self.n_qubits)]
        else:
            self.pool = pool

    def run(
        self,
        grad_tol: float = 1e-2,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> AdaptResult:
        exe = executor or self._executor
        rng = np.random.default_rng(seed)
        n_hea = 2 * self.n_qubits * self.hea_depth
        hea_angles = rng.uniform(-np.pi, np.pi, size=n_hea)
        layers: list[tuple[tuple[int, int], float]] = []

        def build_state(hea_x: np.ndarray, exc: list[tuple[tuple[int, int], float]]) -> np.ndarray:
            st = hea_state(hea_x, self.n_qubits, self.hea_depth)
            for (i, j), th in exc:
                st = apply_excitation_simple(st, i, j, self.n_qubits, th)
            return st / np.linalg.norm(st)

        def energy_fn(hea_x: np.ndarray, exc: list[tuple[tuple[int, int], float]]) -> float:
            st = build_state(hea_x, exc)
            return exe.expectation_state(st, self.h_op, self.n_qubits)

        adapt_steps: list[dict[str, Any]] = []
        total_gradient_evals = 0
        for iter_k in range(self.max_ops):
            best_idx = -1
            best_grad_mag = 0.0
            n_candidates = 0
            grad_evals_this_round = 0

            for idx, (i, j) in enumerate(self.pool):
                if any((pair == (i, j)) for pair, _ in layers):
                    continue
                n_candidates += 1

                def obj(delta: float, ij: tuple[int, int] = (i, j)) -> float:
                    trial = layers + [(ij, float(delta))]
                    return energy_fn(hea_angles, trial)

                g = (obj(1e-3) - obj(-1e-3)) / 2e-3
                grad_evals_this_round += 2
                if abs(g) > best_grad_mag:
                    best_grad_mag = abs(g)
                    best_idx = idx

            step: dict[str, Any] = {
                "iteration": iter_k,
                "n_pool_candidates_scanned": n_candidates,
                "n_gradient_evals": grad_evals_this_round,
                "best_grad_mag": float(best_grad_mag),
                "selected_pair": None,
            }
            adapt_steps.append(step)
            total_gradient_evals += grad_evals_this_round

            if best_idx < 0 or best_grad_mag < grad_tol:
                break
            pair = self.pool[best_idx]

            def full_obj(x: np.ndarray) -> float:
                hea_x = x[:n_hea]
                th = float(x[n_hea])
                trial = layers + [(pair, th)]
                return energy_fn(hea_x, trial)

            x0 = np.concatenate([hea_angles, [0.0]])
            res = minimize(full_obj, x0, method="COBYLA", options={"maxiter": 80})
            hea_angles = np.asarray(res.x[:n_hea], dtype=float)
            layers.append((pair, float(res.x[n_hea])))
            step["selected_pair"] = [int(pair[0]), int(pair[1])]

        e = energy_fn(hea_angles, layers)
        return AdaptResult(
            energy=e,
            pool_indices=[p for p, _ in layers],
            angles_per_layer=[a for _, a in layers],
            meta={
                "hea_angles": hea_angles.tolist(),
                "layers": [(list(p), a) for p, a in layers],
                "adapt_steps": adapt_steps,
                "total_gradient_evals": total_gradient_evals,
            },
        )

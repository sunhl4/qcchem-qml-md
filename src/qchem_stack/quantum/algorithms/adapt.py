from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize

from qchem_stack.quantum.algorithms.base import AlgorithmBase
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import (
    expectation_qubit_operator,
    hea_state,
    qubit_operator_to_sparse,
)

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


from qchem_stack.quantum.algorithms.tolerances import ADAPT_GRAD_TOLERANCE

# Default configuration constants
DEFAULT_MAX_OPS = 4
DEFAULT_HEA_DEPTH = 1
DEFAULT_GRAD_TOL = ADAPT_GRAD_TOLERANCE
DEFAULT_SEED = 0
TETRIS_MAX_OPERATORS_PER_ROUND = 4
COBYLA_MAXITER = 80


@dataclass
class AdaptResult:
    energy: float
    pool_indices: list[int]
    angles_per_layer: list[float]
    meta: dict[str, Any] = field(default_factory=dict)


class FermionicAdaptVQE(AlgorithmBase):
    """ADAPT-VQE loop with commutator gradients and executable operator pools.

    Epistemic bounds: dense statevector only (see docs/quantum_模块风格约定.md §8).
    """

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        pool: list[QubitOperator] | None = None,
        pool_id: str = "fermionic_uccsd",
        max_ops: int = DEFAULT_MAX_OPS,
        hea_depth: int = DEFAULT_HEA_DEPTH,
        tetris_style: bool = False,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        super().__init__()
        self._algorithm_name = "adapt"
        self._report_schema = "algorithm_adapt_report_v1"
        self.hamiltonian = hamiltonian
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self.max_ops = max_ops
        self.hea_depth = hea_depth
        self.pool_id = pool_id
        self.tetris_style = bool(tetris_style)
        self._executor = executor or StatevectorHeaExecutor()
        self.pool = pool or build_registered_operator_pool(pool_id, hamiltonian)

    def build(self, **kwargs: Any) -> FermionicAdaptVQE:
        return cast(
            "FermionicAdaptVQE",
            super().build(pool_id=self.pool_id, tetris_style=self.tetris_style, **kwargs),
        )

    def run(
        self,
        grad_tol: float = DEFAULT_GRAD_TOL,
        seed: int = DEFAULT_SEED,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> AdaptResult:
        self._ensure_built()
        exe = executor or self._executor
        rng = np.random.default_rng(seed)
        n_hea = 2 * self.n_qubits * self.hea_depth
        hea_angles = rng.uniform(-np.pi, np.pi, size=n_hea)
        layers: list[tuple[int, float]] = []
        pool_mats = [qubit_operator_to_sparse(op, self.n_qubits) for op in self.pool]

        def build_state(hea_x: np.ndarray, exc: list[tuple[int, float]]) -> np.ndarray:
            st = hea_state(hea_x, self.n_qubits, self.hea_depth)
            for pool_idx, th in exc:
                st = expm(-1j * float(th) * pool_mats[pool_idx]) @ st
            return cast("np.ndarray", st / np.linalg.norm(st))

        def energy_fn(hea_x: np.ndarray, exc: list[tuple[int, float]]) -> float:
            st = build_state(hea_x, exc)
            return exe.expectation_state(st, self.h_op, self.n_qubits)

        def gradient_commutator(state: np.ndarray, pool_idx: int) -> float:
            op = self.pool[pool_idx]
            comm = self.h_op * op - op * self.h_op
            val = expectation_qubit_operator(state, comm, self.n_qubits)
            return float(abs(np.real(val)))

        adapt_steps: list[dict[str, Any]] = []
        total_gradient_evals = 0
        for iter_k in range(self.max_ops):
            active_state = build_state(hea_angles, layers)
            n_candidates = 0
            grad_map: list[tuple[int, float]] = []
            for idx in range(len(self.pool)):
                if any((pool_idx == idx) for pool_idx, _ in layers):
                    continue
                n_candidates += 1
                grad_map.append((idx, gradient_commutator(active_state, idx)))
            grad_evals_this_round = n_candidates
            grad_map.sort(key=lambda x: x[1], reverse=True)
            best_grad_mag = float(grad_map[0][1]) if grad_map else 0.0

            step: dict[str, Any] = {
                "iteration": iter_k,
                "n_pool_candidates_scanned": n_candidates,
                "n_gradient_evals": grad_evals_this_round,
                "best_grad_mag": float(best_grad_mag),
                "selected_indices": [],
            }
            adapt_steps.append(step)
            total_gradient_evals += grad_evals_this_round

            if not grad_map or best_grad_mag < grad_tol:
                break
            selected_this_round = [grad_map[0][0]]
            if self.tetris_style:
                used_qubits: set[int] = set()
                for idx, g in grad_map:
                    if g < grad_tol:
                        continue
                    term_qubits = {q for term in self.pool[idx].terms for (q, _p) in term}
                    if used_qubits & term_qubits:
                        continue
                    selected_this_round.append(idx)
                    used_qubits |= term_qubits
                    if len(selected_this_round) >= TETRIS_MAX_OPERATORS_PER_ROUND:
                        break

            round_sel = tuple(selected_this_round)

            def full_obj(x: np.ndarray, sel: tuple[int, ...] = round_sel) -> float:
                hea_x = x[:n_hea]
                tail = x[n_hea:]
                trial = list(layers)
                for k, idx in enumerate(sel):
                    trial.append((idx, float(tail[k])))
                return energy_fn(hea_x, trial)

            x0 = np.concatenate([hea_angles, np.zeros(len(selected_this_round), dtype=float)])
            res = minimize(full_obj, x0, method="COBYLA", options={"maxiter": COBYLA_MAXITER})
            hea_angles = np.asarray(res.x[:n_hea], dtype=float)
            for k, idx in enumerate(selected_this_round):
                layers.append((idx, float(res.x[n_hea + k])))
            step["selected_indices"] = [int(x) for x in selected_this_round]

        e = energy_fn(hea_angles, layers)
        out = AdaptResult(
            energy=e,
            pool_indices=[pool_idx for pool_idx, _ in layers],
            angles_per_layer=[a for _, a in layers],
            meta={
                "hea_angles": hea_angles.tolist(),
                "layers": [{"pool_index": int(p), "angle": float(a)} for p, a in layers],
                "adapt_steps": adapt_steps,
                "total_gradient_evals": total_gradient_evals,
                "pool_id": self.pool_id,
                "pool_size": len(self.pool),
                "gradient_mode": "commutator",
                "tetris_style": self.tetris_style,
                "grad_tol_used": float(grad_tol),
            },
        )
        self._set_report(
            metrics={
                "energy": out.energy,
                "n_selected_ops": len(out.pool_indices),
                "total_gradient_evals": total_gradient_evals,
            },
            artifacts={"selected_pool_indices": list(out.pool_indices)},
            diagnostics={"meta": dict(out.meta)},
        )
        return out

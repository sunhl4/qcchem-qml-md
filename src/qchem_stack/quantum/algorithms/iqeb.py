from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.base import AlgorithmBase
from qchem_stack.quantum.algorithms.tolerances import (
    IQEB_ENERGY_TOLERANCE,
    IQEB_POOL_COEFF_SCALE,
)
from qchem_stack.quantum.algorithms.vqe import VQE, VQEResult
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import expectation_qubit_operator, hea_state

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


@dataclass
class IQEBResult:
    energy: float
    selected_pauli_strings: list[str]
    vqe: VQEResult
    meta: dict[str, Any] = field(default_factory=dict)


class IQEBVQE(AlgorithmBase):
    """IQEB-style outer loop with gradient-ranked candidate screening."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        max_rounds: int = 2,
        n_grads: int = 3,
        energy_tolerance: float = IQEB_ENERGY_TOLERANCE,
        pool_id: str = "iqeb_qubit_excitation",
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        super().__init__()
        self._algorithm_name = "iqeb"
        self._report_schema = "algorithm_iqeb_report_v1"
        self.base = hamiltonian
        self.max_rounds = max(1, max_rounds)
        self.n_grads = max(1, int(n_grads))
        self.energy_tolerance = float(energy_tolerance)
        self.pool_id = pool_id
        self.pool = build_registered_operator_pool(pool_id, hamiltonian)
        self._executor = executor

    def run(self, depth: int = 1, seed: int = 0) -> IQEBResult:
        h = deepcopy(self.base.operator)
        selected: list[str] = []
        selected_indices: list[int] = []
        last: VQEResult | None = None
        rounds_meta: list[dict[str, Any]] = []
        prev_energy: float | None = None
        for r in range(self.max_rounds):
            qh = QubitHamiltonian(
                operator=h,
                n_qubits=self.base.n_qubits,
                fermion_space=self.base.fermion_space,
            )
            vqe = VQE(qh, depth=depth, executor=self._executor)
            last = vqe.run(maxiter=120, seed=seed + r)
            state = hea_state(last.angles, self.base.n_qubits, depth)
            grad_map: list[tuple[int, float]] = []
            for idx, op in enumerate(self.pool):
                if idx in selected_indices:
                    continue
                comm = h * op - op * h
                g = float(abs(np.real(expectation_qubit_operator(state, comm, self.base.n_qubits))))
                grad_map.append((idx, g))
            grad_map.sort(key=lambda x: x[1], reverse=True)
            top = grad_map[: self.n_grads]
            rounds_meta.append(
                {
                    "round": r,
                    "energy": float(last.energy),
                    "top_gradients": [{"pool_index": int(i), "gradient": float(g)} for i, g in top],
                }
            )
            if (
                prev_energy is not None
                and abs(float(prev_energy) - float(last.energy)) < self.energy_tolerance
            ):
                break
            if r >= self.max_rounds - 1 or not top:
                break
            best_idx, _ = top[0]
            selected_indices.append(int(best_idx))
            tag = f"pool_{best_idx}_round{r}"
            selected.append(tag)
            h += IQEB_POOL_COEFF_SCALE * self.pool[best_idx]
            prev_energy = float(last.energy)

        if last is None:
            from qchem_stack.exceptions import QuantumAlgorithmError

            raise QuantumAlgorithmError(
                "IQEB optimization failed: no successful VQE rounds completed"
            )

        out = IQEBResult(
            energy=last.energy,
            selected_pauli_strings=selected,
            vqe=last,
            meta={
                "rounds": self.max_rounds,
                "n_grads": self.n_grads,
                "energy_tolerance": self.energy_tolerance,
                "selected_pool_indices": selected_indices,
                "pool_id": self.pool_id,
                "iqeb_rounds": rounds_meta,
            },
        )
        self._set_report(
            metrics={
                "energy": out.energy,
                "rounds": len(rounds_meta),
                "selected_terms": len(selected_indices),
            },
            artifacts={"selected_pool_indices": selected_indices},
            diagnostics={"meta": dict(out.meta)},
        )
        return out

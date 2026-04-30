from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.vqe import VQE, VQEResult

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


@dataclass
class IQEBResult:
    energy: float
    selected_pauli_strings: list[str]
    vqe: VQEResult
    meta: dict[str, Any] = field(default_factory=dict)


class IQEBVQE:
    """IQEB-style outer loop: augment Hamiltonian with small Pauli corrections then re-VQE."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        max_rounds: int = 2,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        self.base = hamiltonian
        self.max_rounds = max(1, max_rounds)
        self._executor = executor

    def run(self, depth: int = 1, seed: int = 0) -> IQEBResult:
        h = deepcopy(self.base.operator)
        selected: list[str] = []
        last: VQEResult | None = None
        for r in range(self.max_rounds):
            qh = QubitHamiltonian(
                operator=h,
                n_qubits=self.base.n_qubits,
                fermion_space=self.base.fermion_space,
            )
            vqe = VQE(qh, depth=depth, executor=self._executor)
            last = vqe.run(maxiter=120, seed=seed + r)
            if r < self.max_rounds - 1:
                tag = f"ZZ_round{r}"
                selected.append(tag)
                h += QubitOperator(((0, "Z"), (1, "Z")), 1e-4 * (-1) ** r)
        assert last is not None
        return IQEBResult(
            energy=last.energy,
            selected_pauli_strings=selected,
            vqe=last,
            meta={"rounds": self.max_rounds},
        )

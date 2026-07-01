"""Hamiltonian expectation computable (HEA / UCCSD + exact or Pauli protocol)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.protocols.ansatz_prep import prepare_statevector
from qchem_stack.protocols.computables.base import EvaluationContext, EvaluationResult
from qchem_stack.quantum.statevector import expectation_qubit_operator

if TYPE_CHECKING:
    from openfermion.ops.operators.qubit_operator import QubitOperator

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


@dataclass
class ExpectationValueComputable:
    """Evaluate ``<psi(angles)|H|psi(angles)>``."""

    name: str
    hamiltonian: QubitOperator
    n_qubits: int
    hea_depth: int = 1
    executor: HamiltonianExpectationExecutor | None = None

    def evaluate(self, ctx: EvaluationContext) -> EvaluationResult:
        ang = np.asarray(ctx.angles, dtype=float)
        if ctx.ansatz_prep is not None:
            psi = prepare_statevector(ctx.ansatz_prep)
            val = float(np.real(expectation_qubit_operator(psi, self.hamiltonian, self.n_qubits)))
            return EvaluationResult(self.name, val, {"path": "ansatz_prep_statevector"})
        if self.executor is None:
            raise ValueError("ExpectationValueComputable requires ansatz_prep or executor")
        val = float(
            self.executor.expectation_hea(
                self.hamiltonian,
                self.n_qubits,
                ang,
                self.hea_depth,
            )
        )
        return EvaluationResult(self.name, val, {"path": "hea_executor"})

    def evaluate_via_protocol_counts(self, protocol_counts: dict[str, object]) -> EvaluationResult:
        exp = protocol_counts.get("expectation")
        if exp is None:
            raise KeyError("protocol_counts missing expectation")
        if not isinstance(exp, (int, float)):
            raise TypeError(f"protocol_counts expectation must be numeric, got {type(exp)!r}")
        return EvaluationResult(self.name, float(exp), {"path": "pauli_protocol"})

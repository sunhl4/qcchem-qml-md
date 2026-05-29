"""QSE H/S matrix computable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.protocols.computables.base import EvaluationContext, EvaluationResult
from qchem_stack.quantum.qse_transition import (
    qse_h_matrix_transition_grouped_pauli_shots,
    qse_h_matrix_transition_qiskit_shots,
    qse_h_s_matrices_exact,
)

if TYPE_CHECKING:
    from openfermion.ops.operators.qubit_operator import QubitOperator


@dataclass
class QSEMatricesComputable:
    name: str
    hamiltonian: QubitOperator
    n_qubits: int
    basis: list[np.ndarray]
    shot_mode: str = "exact"
    shots_per_ij_term: int = 512

    def evaluate(self, ctx: EvaluationContext) -> EvaluationResult:
        rng = ctx.rng or np.random.default_rng(0)
        if self.shot_mode == "pauli_transitions_qiskit":
            h_sym, s_mat, records = qse_h_matrix_transition_qiskit_shots(
                self.basis,
                self.hamiltonian,
                self.n_qubits,
                shots_per_ij_term=int(self.shots_per_ij_term),
            )
            return EvaluationResult(
                self.name,
                {"H": np.asarray(h_sym), "S": np.asarray(s_mat)},
                {
                    "shot_noise_model": "qiskit_histogram_per_ij_term",
                    "n_records": len(records),
                    "transition_records": records,
                    "computable_runtime": "QSEMatricesComputable",
                },
            )
        if self.shot_mode == "pauli_transitions":
            h_sym, s_mat, records = qse_h_matrix_transition_grouped_pauli_shots(
                self.basis,
                self.hamiltonian,
                self.n_qubits,
                shots_per_ij_term=int(self.shots_per_ij_term),
                rng=rng,
            )
            return EvaluationResult(
                self.name,
                {"H": np.asarray(h_sym), "S": np.asarray(s_mat)},
                {
                    "shot_noise_model": "grouped_statevector_shot_simulation_per_ij_term",
                    "n_records": len(records),
                    "transition_records": records,
                    "computable_runtime": "QSEMatricesComputable",
                },
            )
        h_sub, s_sub = qse_h_s_matrices_exact(
            self.basis,
            self.hamiltonian,
            self.n_qubits,
        )
        return EvaluationResult(
            self.name,
            {"H": np.asarray(h_sub), "S": np.asarray(s_sub)},
            {"shot_noise_model": "exact"},
        )

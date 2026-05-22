"""Overlap-squared computable for VQD channels."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qchem_stack.protocols.ansatz_prep import prepare_statevector
from qchem_stack.protocols.computables.base import EvaluationContext, EvaluationResult
from qchem_stack.quantum.algorithms.excited_basis import _overlap_squared_swap_test
from qchem_stack.quantum.statevector import hea_state


@dataclass
class OverlapSquaredComputable:
    name: str
    n_qubits: int
    hea_depth: int
    reference_parameters: np.ndarray
    shots: int = 0

    def evaluate(self, ctx: EvaluationContext) -> EvaluationResult:
        if ctx.ansatz_prep is not None:
            psi_ref = prepare_statevector(
                type(ctx.ansatz_prep)(
                    kind=ctx.ansatz_prep.kind,
                    n_qubits=ctx.ansatz_prep.n_qubits,
                    angles=np.asarray(self.reference_parameters, dtype=float),
                    hea_depth=ctx.ansatz_prep.hea_depth,
                    uccsd_ctx=ctx.ansatz_prep.uccsd_ctx,
                    uccsd_decomposition_mode=ctx.ansatz_prep.uccsd_decomposition_mode,
                )
            )
            psi = prepare_statevector(ctx.ansatz_prep)
        else:
            psi_ref = hea_state(
                np.asarray(self.reference_parameters, dtype=float),
                self.n_qubits,
                self.hea_depth,
            )
            psi = hea_state(np.asarray(ctx.angles, dtype=float), self.n_qubits, self.hea_depth)
        exact = float(abs(np.vdot(psi_ref, psi)) ** 2)
        meta: dict[str, float] = {"overlap_squared_exact": exact}
        if self.shots > 0:
            rng = ctx.rng or np.random.default_rng(0)
            est, se = _overlap_squared_swap_test(psi_ref, psi, int(self.shots), rng)
            meta["overlap_squared_shot_mean"] = float(est)
            meta["overlap_squared_shot_stderr"] = float(se)
        return EvaluationResult(self.name, exact, meta)

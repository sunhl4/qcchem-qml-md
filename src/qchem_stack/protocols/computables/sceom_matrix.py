"""SCEOM M-matrix computable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.protocols.computables.base import EvaluationContext, EvaluationResult
from qchem_stack.quantum.algorithms.sceom import (
    run_sceom_nested_commutator_from_hea,
    run_sceom_nested_commutator_from_uccsd,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class SCEOMMatrixComputable:
    name: str
    hamiltonian: QubitHamiltonian
    subspace_dim: int = 4
    generator_strategy: str = "fermionic_singles_mapped"
    shots_per_matrix_element: int = 0
    self_consistent_rounds: int = 0
    shots_backend: str = "statevector"
    s_generators: list[object] | None = None
    prepare_state: Callable[[np.ndarray], np.ndarray] | None = None
    hea_depth: int = 1

    def evaluate(self, ctx: EvaluationContext) -> EvaluationResult:
        rng = ctx.rng or np.random.default_rng(0)
        extra: dict[str, object] = {}
        gens = self.s_generators if self.s_generators is not None else ctx.extra.get("s_generators")
        if gens is not None:
            extra["s_generators"] = gens
        angles = np.asarray(ctx.angles, dtype=float)
        if self.prepare_state is not None:
            res = run_sceom_nested_commutator_from_uccsd(
                self.hamiltonian,
                angles,
                self.prepare_state,
                subspace_dim=int(self.subspace_dim),
                generator_strategy_yaml=self.generator_strategy,
                shots_per_matrix_element=int(self.shots_per_matrix_element),
                seed=int(rng.integers(0, 2**31)),
                self_consistent_rounds=int(self.self_consistent_rounds),
                shots_backend=str(self.shots_backend),
                **extra,
            )
            variety = "uccsd"
        else:
            depth_raw = ctx.extra.get("hea_depth", self.hea_depth)
            depth = int(depth_raw) if isinstance(depth_raw, int) else self.hea_depth
            res = run_sceom_nested_commutator_from_hea(
                self.hamiltonian,
                angles,
                depth,
                subspace_dim=int(self.subspace_dim),
                generator_strategy_yaml=self.generator_strategy,
                shots_per_matrix_element=int(self.shots_per_matrix_element),
                seed=int(rng.integers(0, 2**31)),
                self_consistent_rounds=int(self.self_consistent_rounds),
                shots_backend=str(self.shots_backend),
                **extra,
            )
            variety = "hea"
        meta = dict(res.meta)
        meta["computable_runtime"] = "SCEOMMatrixComputable"
        meta["sceom_variety"] = variety
        return EvaluationResult(
            self.name,
            {"excitation_energies": list(res.energies), "M": res.meta.get("M_matrix")},
            meta,
        )

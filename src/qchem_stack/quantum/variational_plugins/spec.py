"""Typed contract for plug-in variational stages (pipeline main line)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig


@dataclass
class VariationalRunContext:
    """Everything a variational plug-in needs; no chemistry-backend coupling."""

    cfg: ExperimentConfig
    hamiltonian: QubitHamiltonian
    executor: HamiltonianExpectationExecutor
    seed: int


@dataclass
class VariationalStageOutcome:
    """Stable result surface merged into pipeline output.

    Downstream stages (Pauli protocol, VQD, QSE…) expect ``angles`` to pack the HEA circuit
    (``qchem_stack.quantum.statevector.hea_state``) unless a dedicated extension documents otherwise.
    """

    energy: float
    angles: np.ndarray
    """1-D float parameters for HEA with ``quantum.vqe_depth``."""

    algo_meta: dict[str, Any] = field(default_factory=dict)
    """Flattened metadata merged into pipeline dict (historical keys: ``algorithm``, ``nfev``, …)."""

    algorithm_report: dict[str, Any] | None = None
    """Optional standardized report (e.g. :meth:`AlgorithmBase.generate_report`)."""

    def algo_meta_must_include_algorithm(self, algorithm_id: str) -> dict[str, Any]:
        merged = dict(self.algo_meta)
        merged.setdefault("algorithm", algorithm_id)
        return merged

"""Variational quantum deflation (VQD)."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import numpy as np

from qchem_stack.quantum.algorithms.tolerances import FLOAT_PRECISION_TINY
from qchem_stack.quantum.statevector import hea_state

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

from .excited_vqd_deflation import run_vqd_deflation
from .excited_vqd_helpers import (
    build_vqd_excited_result_meta,
    minimize_vqd_objective,
    pick_vqd_x0,
    prepare_vqd_ground_level,
)

if TYPE_CHECKING:
    from .excited_vqd_types import VQDResult


class VQD:
    """Sequential deflation (Higgott et al., `Quantum 3, 156 (2019)`) with optional three-channel reporting.

    Optimization uses a single classical scalar objective (regularized overlap penalty configurable via
    ``overlap_exponent``). After each level, :func:`_vqd_three_protocol_channels` reports objective /
    overlap / weight statistics analogous to three ``Protocol`` slots (optional shot budgets).

    Optional ``prepare_state`` switches the variational manifold from HEA (:func:`hea_state`) to e.g.
    UCCSD (:meth:`~qchem_stack.quantum.algorithms.uccsd_vqe.UCCSDVQE.prepare_state`).

    **Product / integrator spec (YAML, pipeline wiring, cross-stack meta):** see repository
    ``docs/技术文档_VQD紧缩激发与跨栈对照.md``.
    """

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        n_states: int = 2,
        depth: int = 1,
        penalty_weight: float = 5.0,
        *,
        penalty_weights: list[float] | None = None,
        overlap_exponent: float = 1.0,
        cobyla_maxiter: int = 150,
        optimizer_method: str = "COBYLA",
        prepare_state: Callable[[np.ndarray], np.ndarray] | None = None,
        n_var_parameters: int | None = None,
        parameter_bounds: list[tuple[float, float]] | None = None,
        init_strategy: str = "legacy",
        init_noise_scale: float = 0.15,
        max_overlap_warn: float | None = 0.05,
        overlap_mode: str = "statevector_overlap",
        optimizer_mode: str = "collapsed",
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        self.hamiltonian = hamiltonian
        self.n_states = n_states
        self.depth = depth
        self.penalty_weight = penalty_weight
        self._penalty_weights = list(penalty_weights) if penalty_weights is not None else None
        self.overlap_exponent = float(max(overlap_exponent, 0.05))
        self.cobyla_maxiter = int(max(1, cobyla_maxiter))
        self.optimizer_method = str(optimizer_method).strip().upper()
        self.prepare_state = prepare_state
        self.n_var_parameters = n_var_parameters
        self.parameter_bounds = parameter_bounds
        self.init_strategy = str(init_strategy)
        self.init_noise_scale = float(max(0.0, init_noise_scale))
        self.max_overlap_warn = max_overlap_warn
        self.overlap_mode = str(overlap_mode).strip()
        self.optimizer_mode = str(optimizer_mode).strip().lower()
        if self.overlap_mode not in {
            "statevector_overlap",
            "tangelo_circuit_analogy",
            "deflation_circuit",
        }:
            raise ValueError(
                "VQD overlap_mode must be 'statevector_overlap', "
                "'tangelo_circuit_analogy', or 'deflation_circuit'"
            )
        self._executor = executor

    def _n_params(self) -> int:
        if self.prepare_state is not None:
            if self.n_var_parameters is None:
                raise ValueError("VQD with prepare_state requires n_var_parameters")
            return int(self.n_var_parameters)
        return int(2 * self.hamiltonian.n_qubits * self.depth)

    def _prep(self, x: np.ndarray) -> np.ndarray:
        xv = np.asarray(x, dtype=float).ravel()
        if self.prepare_state is not None:
            g = self.prepare_state(xv)
        else:
            g = hea_state(xv, self.hamiltonian.n_qubits, self.depth)
        g = np.asarray(g, dtype=complex).ravel()
        return cast("np.ndarray", g / (np.linalg.norm(g) + FLOAT_PRECISION_TINY))

    def _resolve_penalties(self) -> list[float]:
        n_exc = max(0, self.n_states - 1)
        if n_exc == 0:
            return []
        if self._penalty_weights is not None:
            if len(self._penalty_weights) != n_exc:
                raise ValueError(
                    "penalty_weights must have length n_states - 1 "
                    f"({n_exc}), got {len(self._penalty_weights)}"
                )
            return [float(x) for x in self._penalty_weights]
        return [float(self.penalty_weight)] * n_exc

    def _pick_x0(self, **kwargs: object) -> np.ndarray:
        return pick_vqd_x0(self, **kwargs)  # type: ignore[arg-type]

    def _minimize(self, objective: Callable[[np.ndarray], float], x0: np.ndarray) -> object:
        return minimize_vqd_objective(self, objective, x0)

    def _prepare_ground_level(self, **kwargs: object):
        return prepare_vqd_ground_level(self, **kwargs)  # type: ignore[arg-type]

    def _build_excited_result_meta(self, **kwargs: object) -> dict:
        return build_vqd_excited_result_meta(self, **kwargs)  # type: ignore[arg-type]

    def run(
        self,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
        *,
        shots_objective: int = 0,
        shots_overlap: int = 0,
        shots_weight: int = 0,
        pauli_grouping: str = "tensor_product",
        ground_angles: np.ndarray | None = None,
        ground_energy: float | None = None,
    ) -> VQDResult:
        """Run VQD. If ``ground_angles`` is set (e.g. from pipeline VQE/ADAPT), skip an inner VQE for level 0."""
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        exe = executor or self._executor or StatevectorHeaExecutor()
        return run_vqd_deflation(
            self,
            exe=exe,
            seed=seed,
            shots_objective=shots_objective,
            shots_overlap=shots_overlap,
            shots_weight=shots_weight,
            pauli_grouping=pauli_grouping,
            ground_angles=ground_angles,
            ground_energy=ground_energy,
        )

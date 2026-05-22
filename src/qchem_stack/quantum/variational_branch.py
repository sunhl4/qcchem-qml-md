"""Shared UCCSD vs HEA variational branch wiring (VQE ground state + VQD prepare_state)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass(frozen=True)
class UccsdVariationalModel:
    """UCCSD cluster parameters for downstream stages (e.g. VQD deflation)."""

    prepare_state: Callable[[np.ndarray], np.ndarray]
    n_params: int
    param_bounds: list[tuple[float, float]]


def _uccsd_instance(
    qh: QubitHamiltonian,
    exe: HamiltonianExpectationExecutor,
    *,
    trotter_steps: int | None,
) -> Any:
    from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE

    if trotter_steps is not None:
        return UCCSDTrotterVQE(
            qh,
            executor=exe,
            n_trotter_steps=int(trotter_steps),
        )
    return UCCSDVQE(qh, executor=exe)


def build_uccsd_variational_model(
    qh: QubitHamiltonian,
    exe: HamiltonianExpectationExecutor,
    *,
    trotter_steps: int | None,
) -> UccsdVariationalModel:
    """Build ``prepare_state`` + parameter bounds for UCCSD-based excited-state stages."""
    ucc = _uccsd_instance(qh, exe, trotter_steps=trotter_steps)
    n_vp = int(ucc.n_params)
    return UccsdVariationalModel(
        prepare_state=ucc.prepare_state,
        n_params=n_vp,
        param_bounds=[(-4.0 * np.pi, 4.0 * np.pi)] * n_vp,
    )


def run_uccsd_vqe_from_config(
    qh: QubitHamiltonian,
    exe: HamiltonianExpectationExecutor,
    *,
    maxiter: int,
    seed: int,
    trotter_steps: int | None,
) -> Any:
    """Run dense or Trotter UCCSD VQE (shared by variational plugin and tests)."""
    ucc = _uccsd_instance(qh, exe, trotter_steps=trotter_steps)
    return ucc.run(maxiter=int(maxiter), seed=int(seed))

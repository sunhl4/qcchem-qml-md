"""Typed contract for plug-in excited-state stages (pipeline sidecars)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import numpy as np

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.chem.pre_quantum_input import PreQuantumInput
    from qchem_stack.config import ExperimentConfig


@dataclass
class ExcitedRunContext:
    """Everything an excited-state plug-in needs; no chemistry-backend coupling."""

    cfg: ExperimentConfig
    hamiltonian: QubitHamiltonian
    executor: HamiltonianExpectationExecutor | None
    seed: int
    ground_angles: np.ndarray
    ground_energy: float
    pre_quantum_input: PreQuantumInput | None = None

    def resolved_hamiltonian(self) -> QubitHamiltonian:
        if self.pre_quantum_input is not None:
            return self.pre_quantum_input.qubit_hamiltonian
        return self.hamiltonian


@dataclass
class ExcitedStageOutcome:
    """Stable result surface merged into pipeline output."""

    bundle_key: str
    bundle: dict[str, Any]

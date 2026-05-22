"""Test helpers for restricted active-space quantum problems."""

from __future__ import annotations

from qchem_stack.chem.molecular_problem import RestrictedActiveSpaceQuantumProblem
from qchem_stack.chem.molecular_problem_build import (
    restricted_active_space_quantum_problem_from_config,
)
from qchem_stack.config import ExperimentConfig

__all__ = ["restricted_quantum_problem_from_config"]


def restricted_quantum_problem_from_config(
    cfg: ExperimentConfig,
) -> RestrictedActiveSpaceQuantumProblem:
    return restricted_active_space_quantum_problem_from_config(cfg)

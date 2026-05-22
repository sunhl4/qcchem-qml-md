"""Orchestration compatibility re-exports for pre-quantum assembly (implementation in ``chem``)."""

from __future__ import annotations

from qchem_stack.chem.pre_quantum_build import (
    build_pre_quantum_input,
    hamiltonian,
    hamiltonian_with_schmidt_context,
    schmidt_hamiltonian_and_context,
)
from qchem_stack.integrations.schmidt_per_fragment_vqe import run_schmidt_per_fragment_vqe

__all__ = [
    "build_pre_quantum_input",
    "hamiltonian",
    "hamiltonian_with_schmidt_context",
    "run_schmidt_per_fragment_vqe",
    "schmidt_hamiltonian_and_context",
]

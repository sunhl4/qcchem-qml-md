"""Orchestration compatibility re-exports for pre-quantum assembly (implementation in ``chem``)."""

from __future__ import annotations

from qchem_stack.chem.embedding.schmidt_variational_sidecar import run_schmidt_per_fragment_vqe
from qchem_stack.chem.pre_quantum_build import (
    build_pre_quantum_input,
    hamiltonian,
    hamiltonian_with_schmidt_context,
    schmidt_hamiltonian_and_context,
)
from qchem_stack.chem.pre_quantum_pyscf_gate import require_pyscf_reference

__all__ = [
    "build_pre_quantum_input",
    "hamiltonian",
    "hamiltonian_with_schmidt_context",
    "require_pyscf_reference",
    "run_schmidt_per_fragment_vqe",
    "schmidt_hamiltonian_and_context",
]

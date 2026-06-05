# pyright: reportUnsupportedDunderAll=false
"""Embedding: Schmidt, DMET, projection, and decomposition-plugin numerics."""

from __future__ import annotations

from qchem_stack.chem.embedding.ao_fragment import mulliken_mo_populations_on_atoms
from qchem_stack.chem.embedding.dmet import (
    DMETContext,
    FragmentSolverProtocol,
    QubitHamiltonianFragmentSolverExact,
    VQEFragmentSolverStub,
)
from qchem_stack.chem.embedding.fragment_solvers.qubit_hamiltonian_vqe import (
    QubitHamiltonianFragmentSolverVQE,
)
from qchem_stack.chem.embedding.projection import ProjectionEmbeddingConfig
from qchem_stack.chem.embedding.projection_hamiltonian import (
    molecular_hamiltonian_fragment_mulliken_projection,
    select_active_mo_indices,
)

__all__ = [
    "DMETContext",
    "FragmentSolverProtocol",
    "ProjectionEmbeddingConfig",
    "QubitHamiltonianFragmentSolverExact",
    "QubitHamiltonianFragmentSolverVQE",
    "VQEFragmentSolverStub",
    "molecular_hamiltonian_fragment_mulliken_projection",
    "mulliken_mo_populations_on_atoms",
    "select_active_mo_indices",
]

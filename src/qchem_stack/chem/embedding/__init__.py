# pyright: reportUnsupportedDunderAll=false
"""Embedding: Schmidt, DMET, projection, and decomposition-plugin numerics.

Public surface: ``DMETContext``, ``ProjectionEmbeddingConfig``, Mulliken projection helpers.
Legacy ``mulliken_mo_populations_on_atoms`` (PySCF-mf entry) emits ``DeprecationWarning``;
prefer ``qchem_stack.chem.embedding.ao_fragment.mulliken_mo_populations_on_atoms`` with an
``AOBasisView``.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.chem.embedding.dmet import (
    DMETContext,
    FragmentSolverProtocol,
    QubitHamiltonianFragmentSolverExact,
    VQEFragmentSolverStub,
)
from qchem_stack.chem.embedding.projection import ProjectionEmbeddingConfig
from qchem_stack.chem.embedding.projection_hamiltonian import (
    molecular_hamiltonian_fragment_mulliken_projection,
    mulliken_mo_populations_on_atoms,
    select_active_mo_indices,
)

__all__ = [
    "DMETContext",
    "FragmentSolverProtocol",
    "ProjectionEmbeddingConfig",
    "molecular_hamiltonian_fragment_mulliken_projection",
    "mulliken_mo_populations_on_atoms",
    "select_active_mo_indices",
    "QubitHamiltonianFragmentSolverExact",
    "QubitHamiltonianFragmentSolverVQE",
    "VQEFragmentSolverStub",
]


def __getattr__(name: str) -> Any:
    if name == "QubitHamiltonianFragmentSolverVQE":
        import warnings

        warnings.warn(
            "qchem_stack.chem.embedding.QubitHamiltonianFragmentSolverVQE is deprecated; "
            "use qchem_stack.integrations.dmet_fragment_solvers instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from qchem_stack.integrations.dmet_fragment_solvers import (
            QubitHamiltonianFragmentSolverVQE,
        )

        return QubitHamiltonianFragmentSolverVQE
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

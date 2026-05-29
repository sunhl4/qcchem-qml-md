"""DMET fragment solver plugin registry (C-02 SPI)."""

from qchem_stack.chem.embedding.fragment_solvers.registry import (
    list_fragment_solver_ids,
    register_fragment_solver,
    resolve_fragment_solver,
)

__all__ = [
    "list_fragment_solver_ids",
    "register_fragment_solver",
    "resolve_fragment_solver",
]

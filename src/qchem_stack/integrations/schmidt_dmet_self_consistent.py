"""Backward-compatible re-exports; canonical implementation in ``chem.embedding``."""

from qchem_stack.chem.embedding.schmidt_dmet_self_consistent import (  # noqa: F401
    FCISchmidtImpuritySolver,
    run_schmidt_density_feedback_cycles,
    run_schmidt_multifragment_density_cycles,
)

__all__ = [
    "FCISchmidtImpuritySolver",
    "run_schmidt_density_feedback_cycles",
    "run_schmidt_multifragment_density_cycles",
]

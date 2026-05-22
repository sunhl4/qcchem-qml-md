"""Backward-compatible re-exports; canonical implementation in ``chem.embedding``."""

from qchem_stack.chem.embedding.dmet_self_consistent import (  # noqa: F401
    DMETBathState,
    DMETFragmentResult,
    DMETSelfConsistencyLoop,
    OneShotEmbeddingDriver,
)

__all__ = [
    "DMETBathState",
    "DMETFragmentResult",
    "DMETSelfConsistencyLoop",
    "OneShotEmbeddingDriver",
]

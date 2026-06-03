"""Re-export DMET self-consistency types from ``chem.embedding`` (deprecated path)."""

from __future__ import annotations

import warnings

warnings.warn(
    "qchem_stack.integrations.dmet_self_consistent is deprecated; import from "
    "qchem_stack.chem.embedding.dmet_self_consistent instead. Removal planned in v0.8.0.",
    DeprecationWarning,
    stacklevel=2,
)

from qchem_stack.chem.embedding.dmet_self_consistent import (  # noqa: E402
    DMETBathState,
    DMETFragmentResult,
    DMETSelfConsistencyLoop,
    OneShotEmbeddingDriver,
    run_dmet_bath_scf_self_consistency_v1,
)

__all__ = [
    "DMETBathState",
    "DMETFragmentResult",
    "DMETSelfConsistencyLoop",
    "OneShotEmbeddingDriver",
    "run_dmet_bath_scf_self_consistency_v1",
]

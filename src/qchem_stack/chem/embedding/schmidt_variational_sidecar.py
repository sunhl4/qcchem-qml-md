"""Deprecated: use ``qchem_stack.integrations.schmidt_per_fragment_vqe``."""

from __future__ import annotations

import warnings
from typing import Any


def __getattr__(name: str) -> Any:
    if name == "run_schmidt_per_fragment_vqe":
        warnings.warn(
            "qchem_stack.chem.embedding.schmidt_variational_sidecar is deprecated; "
            "use qchem_stack.integrations.schmidt_per_fragment_vqe instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        from qchem_stack.integrations.schmidt_per_fragment_vqe import run_schmidt_per_fragment_vqe

        return run_schmidt_per_fragment_vqe
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

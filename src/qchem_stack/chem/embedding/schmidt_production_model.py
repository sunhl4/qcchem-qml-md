"""Core Schmidt production datatypes shared by integral and FCI helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from qchem_stack.exceptions import EmbeddingError

if TYPE_CHECKING:
    import numpy as np


class SchmidtProductionError(EmbeddingError):
    """Raised when embedding inputs are invalid or unsafe for the configured caps."""


@dataclass
class SchmidtImpurityModel:
    """Impurity spatial integrals + bookkeeping for audit / JW."""

    constant: float
    h1: np.ndarray
    h2: np.ndarray
    n_spatial_orbitals: int
    n_alpha_electrons: int
    n_beta_electrons: int
    n_fragment_spatial_orbitals: int
    n_bath_spatial_orbitals: int
    fragment_atom_indices: list[int]
    meta: dict[str, Any] = field(default_factory=dict)
    C_imp_ao: np.ndarray | None = field(default=None, repr=False)
    """AO × impurity MO coefficients (``S``-orthonormal columns); used for density-feedback loops only."""

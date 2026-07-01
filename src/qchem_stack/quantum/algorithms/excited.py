"""Excited-state algorithms (VQD, QSE); re-exports for backward compatibility."""

from __future__ import annotations

from .excited_basis import build_qse_basis_from_vqe_hea
from .excited_qse import QSE, QSEResult
from .excited_vqd import VQD
from .excited_vqd_types import VQDResult
from .qse_solve_helpers import qse_matrices_hs

__all__ = [
    "VQD",
    "VQDResult",
    "QSE",
    "QSEResult",
    "build_qse_basis_from_vqe_hea",
    "qse_matrices_hs",
]

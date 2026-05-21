"""Excited-state algorithms (VQD, QSE); re-exports for backward compatibility."""

from __future__ import annotations

from .excited_basis import build_qse_basis_from_vqe_hea
from .excited_qse import QSE, QSEResult, qse_matrices_hs
from .excited_vqd import VQD, VQDResult

__all__ = [
    "VQD",
    "VQDResult",
    "QSE",
    "QSEResult",
    "build_qse_basis_from_vqe_hea",
    "qse_matrices_hs",
]

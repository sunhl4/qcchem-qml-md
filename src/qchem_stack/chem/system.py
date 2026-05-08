from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class MolecularSystem:
    """Chemical system identity + geometry (Bohr)."""

    symbols: list[str]
    coordinates_bohr: np.ndarray  # shape (n_atoms, 3)
    charge: int = 0
    multiplicity: int = 1
    basis: str = "sto-3g"
    ecp: str | dict[str, str] | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.coordinates_bohr = np.asarray(self.coordinates_bohr, dtype=float)
        if self.coordinates_bohr.shape != (len(self.symbols), 3):
            raise ValueError("coordinates_bohr must be (n_atoms, 3)")


@dataclass
class ReferenceState:
    """Reference for embedding / QSE (e.g. RHF CCSD vectors)."""

    label: str
    mo_coeff: np.ndarray | None = None
    rdm1: np.ndarray | None = None
    meta: dict[str, Any] = field(default_factory=dict)

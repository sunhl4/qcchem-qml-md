"""SCF driver identifiers."""

from __future__ import annotations

from enum import StrEnum


class ScfDriverId(StrEnum):
    PYSCF = "pyscf"
    PSI4 = "psi4"
    PRECOMPUTED = "precomputed"

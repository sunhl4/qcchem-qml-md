"""SCF driver identifiers."""

from __future__ import annotations

from qchem_stack.config._str_enum import StrEnum


class ScfDriverId(StrEnum):
    PYSCF = "pyscf"
    PSI4 = "psi4"
    PRECOMPUTED = "precomputed"

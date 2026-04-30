from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FermionSpace:
    """Active spin-orbital count and symmetry metadata."""

    n_spin_orbitals: int
    n_electrons: int
    symmetry_operators: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

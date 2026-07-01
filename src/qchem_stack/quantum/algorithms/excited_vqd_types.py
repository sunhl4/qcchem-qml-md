"""Typed results for VQD drivers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VQDResult:
    energies: list[float]
    meta: dict[str, Any] = field(default_factory=dict)

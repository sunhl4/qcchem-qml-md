from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SPAMCalibration:
    readout_assignment: list[list[float]] | None = None


def apply_spam(prob_0: float, cal: SPAMCalibration) -> float:
    """Affine readout correction toy."""
    if cal.readout_assignment is None:
        return prob_0
    return min(max(prob_0, 0.0), 1.0)

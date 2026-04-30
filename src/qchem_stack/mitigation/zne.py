from __future__ import annotations


def zne_scale_energy(energy: float, scale: float) -> float:
    """Linear noise extrapolation placeholder: ``E' = E * (1 + 0.01 * (scale - 1))``."""
    return float(energy * (1.0 + 0.01 * (scale - 1.0)))

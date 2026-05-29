from __future__ import annotations

import numpy as np


def zne_scale_energy(energy: float, scale: float) -> float:
    """Linear noise extrapolation placeholder: ``E' = E * (1 + 0.01 * (scale - 1))``."""
    return float(energy * (1.0 + 0.01 * (scale - 1.0)))


def richardson_extrapolation(
    energies: list[float],
    scales: list[float],
    *,
    order: int = 1,
) -> float:
    """Richardson/ZNE extrapolation to zero noise (``scale -> 1`` for unitary noise models).

    Fits a polynomial in ``(s - 1)`` through the provided ``(scale, energy)`` pairs.
    """
    if len(energies) != len(scales) or not energies:
        raise ValueError("energies and scales must be same-length non-empty lists")
    s = np.asarray(scales, dtype=float)
    e = np.asarray(energies, dtype=float)
    x = s - 1.0
    deg = min(int(order), len(energies) - 1)
    if deg < 0:
        return float(e[0])
    coeffs = np.polyfit(x, e, deg=deg)
    return float(np.polyval(coeffs, 0.0))

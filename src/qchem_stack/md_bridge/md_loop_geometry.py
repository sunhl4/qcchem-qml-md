"""Geometry helpers for MD validation loop seeding."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from qchem_stack.md_bridge.md_loop_config import SeedMode
else:
    from qchem_stack.md_bridge.md_loop_config import SeedMode  # noqa: TC001

logger = logging.getLogger(__name__)


def jitter_geometries(
    base_bohr: np.ndarray,
    *,
    n: int,
    sigma_bohr: float,
    rng: np.random.Generator,
) -> list[list[list[float]]]:
    out: list[list[list[float]]] = []
    n_atoms = base_bohr.shape[0]
    for _ in range(int(n)):
        noise = rng.normal(scale=float(sigma_bohr), size=(n_atoms, 3))
        displaced = base_bohr + noise
        out.append(
            [
                [float(displaced[i, 0]), float(displaced[i, 1]), float(displaced[i, 2])]
                for i in range(n_atoms)
            ]
        )
    return out


def bond_stretch_geometries(
    base_bohr: np.ndarray,
    *,
    n: int,
    r_min_bohr: float,
    r_max_bohr: float,
) -> list[list[list[float]]]:
    """Scan bond lengths for a diatomic (H2-friendly); empty list if not 2-atom."""
    pos = np.asarray(base_bohr, dtype=np.float64)
    if pos.shape != (2, 3):
        return []
    delta = pos[1] - pos[0]
    bond = float(np.linalg.norm(delta))
    if bond <= 1.0e-8:
        return []
    axis = delta / bond
    center = 0.5 * (pos[0] + pos[1])
    radii = np.linspace(float(r_min_bohr), float(r_max_bohr), int(n))
    out: list[list[list[float]]] = []
    for r in radii:
        half = 0.5 * float(r)
        p0 = center - half * axis
        p1 = center + half * axis
        out.append(
            [
                [float(p0[0]), float(p0[1]), float(p0[2])],
                [float(p1[0]), float(p1[1]), float(p1[2])],
            ]
        )
    return out


def make_seed_geometries(
    base_bohr: np.ndarray,
    *,
    n: int,
    mode: SeedMode,
    sigma_bohr: float,
    bond_min_bohr: float,
    bond_max_bohr: float,
    rng: np.random.Generator,
) -> list[list[list[float]]]:
    if n <= 0:
        return []
    if mode == "bond_stretch":
        stretched = bond_stretch_geometries(
            base_bohr,
            n=n,
            r_min_bohr=bond_min_bohr,
            r_max_bohr=bond_max_bohr,
        )
        if stretched:
            return stretched
        logger.warning(
            "seed_mode=bond_stretch requested but geometry is not diatomic; falling back to jitter"
        )
    return jitter_geometries(base_bohr, n=n, sigma_bohr=sigma_bohr, rng=rng)

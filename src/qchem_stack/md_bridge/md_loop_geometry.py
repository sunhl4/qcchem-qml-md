"""Geometry helpers for MD validation loop seeding."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

if TYPE_CHECKING:
    from qchem_stack.md_bridge.md_loop_config import SeedMode
else:
    from qchem_stack.md_bridge.md_loop_config import SeedMode  # noqa: TC001

logger = logging.getLogger(__name__)

_BOHR_PER_ANGSTROM = 1.0 / 0.529177210903
BondRegime = Literal["bound", "dissociating", "beyond_cutoff", "unknown"]


def angstrom_to_bohr(angstrom: float) -> float:
    return float(angstrom) * _BOHR_PER_ANGSTROM


def resolve_cutoff_bohr(cutoff_ang: float | None, *, default_ang: float = 6.0) -> float:
    """Neighbor-list / interaction cutoff in Bohr (qmlff default 6 Å)."""
    return angstrom_to_bohr(float(default_ang if cutoff_ang is None else cutoff_ang))


def diatomic_bond_bohr(positions_bohr: Any) -> float | None:
    """Return H–H (or general diatomic) bond length in Bohr; ``None`` if not 2-atom."""
    pos = np.asarray(positions_bohr, dtype=np.float64)
    if pos.ndim != 2 or pos.shape != (2, 3):
        return None
    return float(np.linalg.norm(pos[1] - pos[0]))


def classify_bond_regime(
    bond_bohr: float | None,
    *,
    dissociation_bond_bohr: float,
    cutoff_bohr: float,
) -> BondRegime:
    """Classify a bond relative to chemistry dissociation and FF cutoff.

    - ``bound``: R < dissociation threshold (molecular / pre-dissociation).
    - ``dissociating``: dissociation ≤ R ≤ cutoff — interactions may still be
      nonzero inside the force-field cutoff; useful for asymptote learning.
    - ``beyond_cutoff``: R > cutoff — neighbor list drops the pair; do **not**
      merge into training (no pair interaction left to learn from MD blow-ups).
    """
    if bond_bohr is None or not np.isfinite(bond_bohr):
        return "unknown"
    r = float(bond_bohr)
    if r > float(cutoff_bohr):
        return "beyond_cutoff"
    if r >= float(dissociation_bond_bohr):
        return "dissociating"
    return "bound"


def resolve_max_train_bond_bohr(
    *,
    max_train_bond_bohr: float | None,
    cutoff_ang: float | None,
    cutoff_fraction: float = 0.95,
) -> float:
    """Max bond accepted into the training set.

    Defaults to ``cutoff_fraction * cutoff`` so post-dissociation geometries
    *inside* the interaction range are kept, while far-separated MD debris
    beyond the cutoff is rejected.
    """
    cutoff_b = resolve_cutoff_bohr(cutoff_ang)
    auto = float(cutoff_fraction) * cutoff_b
    if max_train_bond_bohr is None:
        return auto
    return float(min(float(max_train_bond_bohr), auto))


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


def geometries_at_bond_lengths(
    base_bohr: np.ndarray,
    radii_bohr: list[float] | np.ndarray,
) -> list[list[list[float]]]:
    """Place a diatomic at explicit bond lengths (Bohr); empty if not 2-atom."""
    pos = np.asarray(base_bohr, dtype=np.float64)
    if pos.shape != (2, 3):
        return []
    delta = pos[1] - pos[0]
    bond = float(np.linalg.norm(delta))
    if bond <= 1.0e-8:
        return []
    axis = delta / bond
    center = 0.5 * (pos[0] + pos[1])
    out: list[list[list[float]]] = []
    for r in np.asarray(radii_bohr, dtype=np.float64).ravel():
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


def make_round_bond_schedule(
    *,
    n_rounds: int,
    bonds_per_round: int,
    r_min_bohr: float,
    r_max_bohr: float,
    seed: int = 0,
) -> list[list[float]]:
    """Build per-round bond lengths that differ across rounds.

    Points sit on half-integer bins of ``[r_min, r_max]`` (complementary to a
    uniform seed linspace), then are shuffled so consecutive rounds sample
    well-separated stretches rather than a monotonic walk.
    """
    n_rounds = int(n_rounds)
    bonds_per_round = int(bonds_per_round)
    if n_rounds <= 0 or bonds_per_round <= 0:
        return [[] for _ in range(max(n_rounds, 0))]
    n = n_rounds * bonds_per_round
    # Mid-bin samples: distinct from seed linspace endpoints when seed uses n_seed points.
    radii = float(r_min_bohr) + (float(r_max_bohr) - float(r_min_bohr)) * (
        np.arange(n, dtype=np.float64) + 0.5
    ) / float(n)
    rng = np.random.default_rng(int(seed))
    radii = radii[rng.permutation(n)]
    schedule: list[list[float]] = []
    for i in range(n_rounds):
        chunk = radii[i * bonds_per_round : (i + 1) * bonds_per_round]
        schedule.append([float(x) for x in chunk])
    return schedule


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

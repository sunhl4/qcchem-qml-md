"""Unit tests for MD loop geometry/summary helpers."""

from __future__ import annotations

import numpy as np

from qchem_stack.md_bridge.md_loop_geometry import (
    bond_stretch_geometries,
    jitter_geometries,
    make_seed_geometries,
)


def test_jitter_geometries_count_and_shape() -> None:
    base = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]])
    rng = np.random.default_rng(0)
    geoms = jitter_geometries(base, n=3, sigma_bohr=0.01, rng=rng)
    assert len(geoms) == 3
    assert all(len(g) == 2 and len(g[0]) == 3 for g in geoms)


def test_bond_stretch_geometries_diatomic() -> None:
    base = np.array([[0.0, 0.0, -0.5], [0.0, 0.0, 0.5]])
    geoms = bond_stretch_geometries(base, n=4, r_min_bohr=1.0, r_max_bohr=2.0)
    assert len(geoms) == 4


def test_make_seed_geometries_empty_n() -> None:
    base = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]])
    rng = np.random.default_rng(0)
    assert (
        make_seed_geometries(
            base,
            n=0,
            mode="jitter",
            sigma_bohr=0.01,
            bond_min_bohr=1.0,
            bond_max_bohr=2.0,
            rng=rng,
        )
        == []
    )


def test_bond_stretch_zero_length_returns_empty() -> None:
    base = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]])
    assert bond_stretch_geometries(base, n=3, r_min_bohr=1.0, r_max_bohr=2.0) == []


def test_make_seed_geometries_bond_stretch_fallback_to_jitter() -> None:
    base = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    rng = np.random.default_rng(0)
    geoms = make_seed_geometries(
        base,
        n=2,
        mode="bond_stretch",
        sigma_bohr=0.01,
        bond_min_bohr=1.0,
        bond_max_bohr=2.0,
        rng=rng,
    )
    assert len(geoms) == 2

"""Unit tests for MD loop geometry/summary helpers."""

from __future__ import annotations

import numpy as np

from qchem_stack.md_bridge.md_loop_config import MdValidationLoopConfig
from qchem_stack.md_bridge.md_loop_geometry import (
    bond_stretch_geometries,
    classify_bond_regime,
    diatomic_bond_bohr,
    geometries_at_bond_lengths,
    jitter_geometries,
    make_round_bond_schedule,
    make_seed_geometries,
    resolve_cutoff_bohr,
    resolve_max_train_bond_bohr,
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


def test_make_round_bond_schedule_unique_and_sized() -> None:
    schedule = make_round_bond_schedule(
        n_rounds=10,
        bonds_per_round=2,
        r_min_bohr=0.8,
        r_max_bohr=2.4,
        seed=1,
    )
    assert len(schedule) == 10
    assert all(len(chunk) == 2 for chunk in schedule)
    flat = [r for chunk in schedule for r in chunk]
    assert len(flat) == 20
    assert len({round(x, 8) for x in flat}) == 20
    assert min(flat) > 0.8 and max(flat) < 2.4


def test_geometries_at_bond_lengths() -> None:
    base = np.array([[0.0, 0.0, -0.5], [0.0, 0.0, 0.5]])
    geoms = geometries_at_bond_lengths(base, [1.2, 1.8])
    assert len(geoms) == 2
    r0 = np.linalg.norm(np.asarray(geoms[0][1]) - np.asarray(geoms[0][0]))
    assert abs(r0 - 1.2) < 1e-8


def test_bond_regime_vs_cutoff() -> None:
    cutoff = resolve_cutoff_bohr(6.0)
    assert classify_bond_regime(1.4, dissociation_bond_bohr=3.0, cutoff_bohr=cutoff) == "bound"
    assert (
        classify_bond_regime(4.0, dissociation_bond_bohr=3.0, cutoff_bohr=cutoff) == "dissociating"
    )
    assert (
        classify_bond_regime(cutoff + 1.0, dissociation_bond_bohr=3.0, cutoff_bohr=cutoff)
        == "beyond_cutoff"
    )
    max_b = resolve_max_train_bond_bohr(max_train_bond_bohr=None, cutoff_ang=6.0)
    assert max_b < cutoff
    assert diatomic_bond_bohr([[0, 0, 0], [0, 0, 2.0]]) == 2.0


def test_staged_tolerance() -> None:
    cfg = MdValidationLoopConfig(
        energy_tolerance_hartree=5e-4,
        tolerance_stage1_hartree=0.05,
        tolerance_stage1_until_round=15,
        tolerance_stage2_hartree=0.01,
        tolerance_stage2_until_round=30,
    )
    assert cfg.resolve_round_tolerance(1) == 0.05
    assert cfg.resolve_round_tolerance(15) == 0.05
    assert cfg.resolve_round_tolerance(16) == 0.01
    assert cfg.resolve_round_tolerance(30) == 0.01
    assert cfg.resolve_round_tolerance(31) == 5e-4


def test_p0p2_config_loads() -> None:
    from pathlib import Path

    cfg = MdValidationLoopConfig.from_yaml(
        Path(__file__).resolve().parents[2] / "configs/example_h2_qmlff_bondscan_ol_p0p2.yaml"
    )
    assert cfg.pretrain_epochs == 250
    assert cfg.max_rounds == 40
    assert cfg.energy_normalization == "subtract_mean"
    assert cfg.n_seed_geometries >= 24
    assert cfg.cutoff_ang == 6.0
    assert cfg.dissociation_bond_bohr == 3.0

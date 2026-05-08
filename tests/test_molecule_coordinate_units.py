"""Molecule coordinate_unit (Å vs Bohr) and legacy ``coordinates_bohr`` YAML key."""

from __future__ import annotations

import numpy as np
import yaml

from qchem_stack.config import ANGSTROM_TO_BOHR, MoleculeSpec, load_experiment_config


def test_legacy_coordinates_bohr_key_defaults_to_bohr_unit() -> None:
    m = MoleculeSpec.model_validate(
        {
            "symbols": ["H", "H"],
            "coordinates_bohr": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        }
    )
    assert m.coordinate_unit == "bohr"
    np.testing.assert_allclose(m.coordinates_in_bohr(), [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]])


def test_coordinates_key_defaults_to_angstrom() -> None:
    m = MoleculeSpec(symbols=["H", "H"], coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]])
    assert m.coordinate_unit == "angstrom"
    np.testing.assert_allclose(
        m.coordinates_in_bohr(),
        np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4 * ANGSTROM_TO_BOHR]], dtype=float),
    )


def test_explicit_coordinates_with_bohr_unit() -> None:
    m = MoleculeSpec(
        symbols=["H", "H"],
        coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        coordinate_unit="bohr",
    )
    np.testing.assert_allclose(m.coordinates_in_bohr(), [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]])


def test_constructor_kwarg_coordinates_bohr_sets_bohr() -> None:
    m = MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 2.0]])
    assert m.coordinate_unit == "bohr"
    np.testing.assert_allclose(m.coordinates, [[0.0, 0.0, 0.0], [0.0, 0.0, 2.0]])


def test_yaml_molecule_coordinates_bohr_alias_infers_bohr() -> None:
    raw = yaml.safe_load(
        """
symbols: [H, H]
coordinates_bohr:
  - [0, 0, 0]
  - [0, 0, 1.4]
basis: sto-3g
"""
    )
    ml = MoleculeSpec.model_validate(raw)
    assert ml.coordinate_unit == "bohr"


def test_example_h2_config_legacy_geometry_unchanged_in_bohr() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    np.testing.assert_allclose(
        cfg.molecule.coordinates_in_bohr(),
        np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]], dtype=float),
    )

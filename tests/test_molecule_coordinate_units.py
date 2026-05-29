"""Molecule coordinate_unit (Å vs Bohr) and canonical ``coordinates`` YAML key."""

from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from qchem_stack.config import ANGSTROM_TO_BOHR, MoleculeSpec, load_experiment_config
from tests.helpers.paths import configs_path


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


def test_rejects_legacy_coordinates_bohr_key() -> None:
    with pytest.raises(ValidationError):
        MoleculeSpec.model_validate(
            {
                "symbols": ["H", "H"],
                "coordinates_bohr": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
            }
        )


def test_example_h2_config_geometry_in_bohr() -> None:

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    np.testing.assert_allclose(
        cfg.molecule.coordinates_in_bohr(),
        np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]], dtype=float),
    )

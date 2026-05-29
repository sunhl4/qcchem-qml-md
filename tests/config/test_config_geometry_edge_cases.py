"""Molecule geometry edge-case validation."""

from __future__ import annotations

import pytest

from qchem_stack.config import MoleculeSpec


def test_molecule_requires_coordinates_or_zmatrix() -> None:
    with pytest.raises(ValueError, match="requires either coordinates or a non-empty zmatrix"):
        MoleculeSpec(symbols=["H", "H"])


def test_coordinates_and_zmatrix_mutually_exclusive() -> None:
    with pytest.raises(ValueError, match="mutually exclusive"):
        MoleculeSpec(
            symbols=["H", "H"],
            coordinates=[[0, 0, 0], [0, 0, 1.0]],
            zmatrix="H\nH 1 r",
        )


def test_coordinates_converted_to_bohr() -> None:
    mol = MoleculeSpec(
        symbols=["H"],
        coordinates=[[0, 0, 0]],
        coordinate_unit="angstrom",
    )
    pos = mol.coordinates_in_bohr()
    assert pos.shape == (1, 3)
    assert float(pos[0, 0]) == 0.0

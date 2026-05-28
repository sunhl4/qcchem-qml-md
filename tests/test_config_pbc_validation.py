"""PBC cell and k-mesh validation."""

from __future__ import annotations

import pytest

from qchem_stack.config.chemistry_extended import ChemistryExtendedSpec
from qchem_stack.config.chemistry_extended_specs import ChemistryPbcSpec


def test_pbc_kpoint_mesh_must_have_three_positive_integers() -> None:
    with pytest.raises(ValueError, match="kpoint_mesh"):
        ChemistryExtendedSpec(pbc=ChemistryPbcSpec(kpoint_mesh=[1, 2]))


def test_pbc_cell_vectors_must_be_3x3() -> None:
    with pytest.raises(ValueError, match="cell_vectors_bohr"):
        ChemistryExtendedSpec(
            pbc=ChemistryPbcSpec(
                kpoint_mesh=[1, 1, 1],
                cell_vectors_bohr=[[1.0, 0.0], [0.0, 1.0], [0.0, 0.0]],
            )
        )


def test_pbc_cell_vectors_must_be_nonsingular() -> None:
    with pytest.raises(ValueError, match="non-singular"):
        ChemistryExtendedSpec(
            pbc=ChemistryPbcSpec(
                kpoint_mesh=[1, 1, 1],
                cell_vectors_bohr=[
                    [1.0, 0.0, 0.0],
                    [1.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                ],
            )
        )

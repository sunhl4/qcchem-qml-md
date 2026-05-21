"""Cross-field validation helpers for :mod:`qchem_stack.config.chemistry_extended`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chemistry_extended import ChemistryExtendedSpec

PBC_MESH_DIM = 3


def validate_pbc_mesh_and_cell(spec: ChemistryExtendedSpec) -> None:
    pbc = spec.pbc
    if len(pbc.kpoint_mesh) != PBC_MESH_DIM or any(value < 1 for value in pbc.kpoint_mesh):
        raise ValueError(
            f"chemistry_extended.pbc.kpoint_mesh must contain {PBC_MESH_DIM} integers >= 1."
        )
    cell = pbc.cell_vectors_bohr
    if cell is None:
        return
    if len(cell) != PBC_MESH_DIM or any(len(row) != PBC_MESH_DIM for row in cell):
        raise ValueError(
            f"chemistry_extended.pbc.cell_vectors_bohr must be a {PBC_MESH_DIM}×{PBC_MESH_DIM} matrix (Bohr)."
        )

    import numpy as np

    matrix = np.asarray(cell, dtype=float)
    if abs(float(np.linalg.det(matrix))) < 1e-12:
        raise ValueError("chemistry_extended.pbc.cell_vectors_bohr must be non-singular.")

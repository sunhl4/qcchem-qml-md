"""Cross-field validation helpers for :mod:`qchem_stack.config.chemistry_extended`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .chemistry_extended import ChemistryExtendedSpec


PBC_MESH_DIM = 3


def validate_pbc_mesh_and_cell(spec: ChemistryExtendedSpec) -> None:
    pbc = spec.pbc_cell_vectors_bohr
    if len(spec.pbc_kpoint_mesh) != PBC_MESH_DIM or any(
        value < 1 for value in spec.pbc_kpoint_mesh
    ):
        raise ValueError(
            f"chemistry_extended.pbc_kpoint_mesh must contain {PBC_MESH_DIM} integers >= 1."
        )
    if pbc is None:
        return
    if len(pbc) != PBC_MESH_DIM or any(len(row) != PBC_MESH_DIM for row in pbc):
        raise ValueError(
            f"chemistry_extended.pbc_cell_vectors_bohr must be a {PBC_MESH_DIM}×{PBC_MESH_DIM} matrix (Bohr)."
        )

    import numpy as np

    matrix = np.asarray(pbc, dtype=float)
    if abs(float(np.linalg.det(matrix))) < 1e-12:
        raise ValueError("chemistry_extended.pbc_cell_vectors_bohr must be non-singular.")
    if spec.pbc_active_space_kpoint_index < 0:
        raise ValueError("chemistry_extended.pbc_active_space_kpoint_index must be >= 0.")

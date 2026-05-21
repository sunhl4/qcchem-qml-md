"""AO-fragment helpers using :class:`~qchem_stack.chem.bridges.ao_basis_view.AOBasisView`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.exceptions import EmbeddingError

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.ao_basis_view import AOBasisView


def atom_ao_ranges(ao: AOBasisView) -> list[tuple[int, int]]:
    return list(ao.aoslice_by_atom())


def fragment_ao_indices(ao: AOBasisView, atom_indices: list[int]) -> list[int]:
    if not atom_indices:
        raise EmbeddingError("fragment_atom_indices must be non-empty.")
    if min(atom_indices) < 0 or max(atom_indices) >= ao.n_atom:
        raise EmbeddingError(
            f"atom_indices must be valid 0-based atom indices for n_atom={ao.n_atom}."
        )
    ranges = atom_ao_ranges(ao)
    idx: list[int] = []
    for ia in atom_indices:
        p0, p1 = ranges[ia]
        idx.extend(range(p0, p1))
    return sorted(set(idx))


def mulliken_mo_populations_on_atoms(
    ao: AOBasisView,
    mo: np.ndarray,
    atom_indices: list[int],
) -> np.ndarray:
    S = ao.overlap_ao()
    mo_r = np.asarray(mo, dtype=float)
    frag_mask = np.zeros(ao.nao, dtype=bool)
    for i in fragment_ao_indices(ao, atom_indices):
        frag_mask[i] = True
    SC = S @ mo_r
    nmo = mo_r.shape[1]
    w = np.empty(nmo, dtype=float)
    for j in range(nmo):
        w[j] = float(np.sum(mo_r[frag_mask, j] * SC[frag_mask, j]))
    return w

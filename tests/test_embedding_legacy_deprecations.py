"""Embedding legacy API deprecation contracts."""

from __future__ import annotations

import warnings

import numpy as np
import pytest


@pytest.mark.pyscf
def test_mulliken_mo_populations_on_atoms_deprecation_warning() -> None:
    pytest.importorskip("pyscf")
    from pyscf import gto, scf

    from qchem_stack.chem.embedding import mulliken_mo_populations_on_atoms

    mol = gto.M(atom="H 0 0 0; H 0 0 1.4", basis="sto-3g")
    mf = scf.RHF(mol)
    mf.kernel()
    mo = np.asarray(mf.mo_coeff, dtype=float)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        weights = mulliken_mo_populations_on_atoms(mf, mo, atom_indices=[0, 1])
    assert weights.shape == (mo.shape[1],)
    assert any(
        issubclass(w.category, DeprecationWarning)
        and "mulliken_mo_populations_on_atoms" in str(w.message)
        for w in caught
    )

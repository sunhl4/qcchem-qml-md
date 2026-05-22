from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.chem.integral_convention import restore_packed_mo_eri_chemist


def test_restore_packed_mo_eri_matches_pyscf() -> None:
    pytest.importorskip("pyscf")
    from pyscf import ao2mo, gto, scf

    mol = gto.M(atom="H 0 0 0; H 0 0 0.74", basis="sto-3g")
    mf = scf.RHF(mol).run(verbose=0)
    norb = mf.mo_coeff.shape[1]
    packed = ao2mo.kernel(mf._eri, mf.mo_coeff, compact=True)
    ref = ao2mo.restore(1, packed, norb)
    ours = restore_packed_mo_eri_chemist(packed, norb)
    assert ours.shape == ref.shape
    assert np.max(np.abs(ours - ref)) < 1e-12


def test_restore_packed_mo_eri_passes_through_dense() -> None:
    dense = np.arange(16, dtype=float).reshape(2, 2, 2, 2)
    out = restore_packed_mo_eri_chemist(dense, 2)
    assert np.array_equal(out, dense)

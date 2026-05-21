"""Unit tests for Psi4 reference API helpers (no SCF required)."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("psi4")
from qchem_stack.chem.integrals.psi4_reference_api import (
    psi4_aoslice_by_atom,
    psi4_fock_ao,
    psi4_hcore_ao,
    psi4_nao,
    psi4_nmo,
    psi4_overlap_ao,
    psi4_set_ca,
)


def test_psi4_reference_api_h2_sto3g() -> None:
    import psi4

    psi4.set_options({"basis": "sto-3g"})
    mol = psi4.geometry("\n0 1\nH 0 0 -0.7\nH 0 0 0.7\nunits bohr\nsymmetry c1\n")
    _e, rhf = psi4.energy("scf", molecule=mol, return_wfn=True)
    assert psi4_nao(rhf) == 2
    assert psi4_nmo(rhf) == 2
    assert psi4_overlap_ao(rhf).shape == (2, 2)
    assert psi4_hcore_ao(rhf).shape == (2, 2)
    assert psi4_fock_ao(rhf).shape == (2, 2)
    assert psi4_aoslice_by_atom(rhf) == [(0, 1), (1, 2)]
    mo = np.asarray(rhf.Ca(), dtype=float)
    mo[0, 0] *= -1.0
    psi4_set_ca(rhf, mo)
    assert np.allclose(np.asarray(rhf.Ca(), dtype=float), mo)

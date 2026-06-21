from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.chem.bridges.ao_basis_view import PySCFAOBasisView, ao_basis_view_from_reference
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.system import MolecularSystem


def test_pyscf_ao_basis_view_from_reference() -> None:
    pytest.importorskip("pyscf")
    from pyscf import gto, scf

    mol = gto.M(atom="H 0 0 0; H 0 0 1.4", basis="sto-3g", unit="Bohr")
    mf = scf.RHF(mol).run()
    ref = ClassicalMeanFieldReference(
        mf=mf,
        e_tot=float(mf.e_tot),
        mo_energy=np.asarray(mf.mo_energy, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H", "H"],
            coordinates_bohr=np.asarray([[0, 0, 0], [0, 0, 1.4]], dtype=float),
            basis="sto-3g",
        ),
        driver_meta={"upstream_classical_software_tag": "pyscf"},
    )
    ao = ao_basis_view_from_reference(ref)
    assert ao.n_atom == 2
    assert ao.nao == mol.nao_nr()
    assert ao.overlap_ao().shape == (ao.nao, ao.nao)
    assert isinstance(ao, PySCFAOBasisView)

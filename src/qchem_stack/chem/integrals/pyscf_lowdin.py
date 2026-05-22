from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.driver_meta import fork_driver_meta
from qchem_stack.chem.bridges.lowdin import build_lowdin_tensors
from qchem_stack.chem.systems.pyscf_views import PySCFLowdinSystem

if TYPE_CHECKING:
    from qchem_stack.chem.system import MolecularSystem


def build_lowdin_system_from_rhf(
    rhf: Any, *, molecular_system: MolecularSystem
) -> PySCFLowdinSystem:
    """Build Löwdin-orthogonal AO integrals + 1-RDM from a PySCF mean-field reference."""
    mf = rhf.mf
    mol = mf.mol
    s = np.asarray(mf.get_ovlp(), dtype=float)
    hcore = np.asarray(mf.get_hcore(), dtype=float)
    lowdin = build_lowdin_tensors(s, hcore, mf.make_rdm1())
    n_ao = int(hcore.shape[0])
    eri_ao = np.asarray(mol.intor("int2e", aosym="s1"), dtype=float).reshape(n_ao, n_ao, n_ao, n_ao)
    h2_low = np.einsum(
        "pa,qb,rc,sd,pqrs->abcd",
        lowdin.c_low,
        lowdin.c_low,
        lowdin.c_low,
        lowdin.c_low,
        eri_ao,
        optimize=True,
    )
    meta = fork_driver_meta(getattr(rhf, "driver_meta", {}))
    meta["integral_representation"] = "lowdin_orth_ao"
    meta["lowdin_basis_transform"] = "s^-1/2"
    return PySCFLowdinSystem(
        constant=float(mol.energy_nuc()),
        h1_spatial=np.asarray(lowdin.h1_low, dtype=float),
        h2_spatial=np.asarray(h2_low, dtype=float),
        rdm1_spatial=np.asarray(lowdin.dm_low, dtype=float),
        molecular_system=molecular_system,
        driver_meta=meta,
    )

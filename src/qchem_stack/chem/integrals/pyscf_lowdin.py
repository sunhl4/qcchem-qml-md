from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

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
    # C_lowdin^T S C_lowdin = I
    evals, evecs = np.linalg.eigh(s)
    if np.min(evals) <= 1e-12:
        raise ValueError("AO overlap matrix is near singular; cannot build stable Lowdin basis.")
    c_low = np.asarray(evecs @ np.diag(evals**-0.5) @ evecs.T, dtype=float)
    hcore = np.asarray(mf.get_hcore(), dtype=float)
    h1_low = np.einsum("pi,pq,qj->ij", c_low, hcore, c_low, optimize=True)
    n_ao = int(hcore.shape[0])
    eri_ao = np.asarray(mol.intor("int2e", aosym="s1"), dtype=float).reshape(n_ao, n_ao, n_ao, n_ao)
    h2_low = np.einsum("pa,qb,rc,sd,pqrs->abcd", c_low, c_low, c_low, c_low, eri_ao, optimize=True)
    dm_ao_raw = mf.make_rdm1()
    if isinstance(dm_ao_raw, (tuple, list)):
        dm_ao = np.asarray(dm_ao_raw[0], dtype=float) + np.asarray(dm_ao_raw[1], dtype=float)
    else:
        dm_ao = np.asarray(dm_ao_raw, dtype=float)
    c_inv = np.linalg.inv(c_low)
    dm_low = np.asarray(c_inv @ dm_ao @ c_inv.T, dtype=float)
    meta = dict(getattr(rhf, "driver_meta", {}) or {})
    meta["integral_representation"] = "lowdin_orth_ao"
    meta["lowdin_basis_transform"] = "s^-1/2"
    return PySCFLowdinSystem(
        constant=float(mol.energy_nuc()),
        h1_spatial=np.asarray(h1_low, dtype=float),
        h2_spatial=np.asarray(h2_low, dtype=float),
        rdm1_spatial=np.asarray(dm_low, dtype=float),
        molecular_system=molecular_system,
        driver_meta=meta,
    )

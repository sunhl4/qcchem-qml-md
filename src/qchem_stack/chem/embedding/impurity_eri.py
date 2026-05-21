"""Transform AO ERIs to an impurity MO basis (PySCF ao2mo or Psi4 MintsHelper)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.chem.bridges.ao_basis_view import (
    AOBasisView,
    Psi4AOBasisView,
    PySCFAOBasisView,
)
from qchem_stack.chem.embedding.psi4_mo_eri import chemist_eri_mo_from_psi4_wfn

if TYPE_CHECKING:
    from qchem_stack.chem.system import MolecularSystem


def impurity_eri_chemist(
    ao: AOBasisView,
    C_imp: np.ndarray,
    *,
    molecular_system: MolecularSystem,
) -> np.ndarray:
    """Return rank-4 chemist ERIs in the impurity MO basis."""
    from pyscf import ao2mo

    C = np.asarray(C_imp, dtype=float)
    n_imp = int(C.shape[1])
    if isinstance(ao, PySCFAOBasisView):
        mol = ao.raw_handle().mol
        return np.asarray(
            ao2mo.restore(1, ao2mo.full(mol, C, compact=False), n_imp),
            dtype=float,
        )
    if isinstance(ao, Psi4AOBasisView):
        return chemist_eri_mo_from_psi4_wfn(ao.raw_handle(), C)
    raise ValueError(
        f"impurity_eri_chemist requires PySCFAOBasisView or Psi4AOBasisView (got {type(ao)!r})."
    )

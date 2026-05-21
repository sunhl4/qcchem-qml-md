"""Transform Psi4 AO ERIs to a chemist MO basis (same index convention as PySCF ``ao2mo``)."""

from __future__ import annotations

from typing import Any

import numpy as np


def chemist_eri_mo_from_psi4_wfn(
    wfn: Any,
    C_mo: np.ndarray,
) -> np.ndarray:
    """Return ``(nmo, nmo, nmo, nmo)`` chemist ERIs in columns of ``C_mo``."""
    from qchem_stack.chem.integrals.psi4_reference_api import psi4_ao_eri_chemist

    eri_ao = psi4_ao_eri_chemist(wfn)
    C = np.asarray(C_mo, dtype=float)
    return np.asarray(
        np.einsum("pi,qj,rk,sl,pqrs->ijkl", C, C, C, C, eri_ao, optimize=True),
        dtype=float,
    )

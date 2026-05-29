"""PySCF MO ERI layout → OpenFermion / ``spinorb_from_spatial`` ordering.

Active-space exporters apply ``numpy.transpose(eri, (0, 2, 3, 1))`` to PySCF MO integrals
before :func:`openfermion.chem.molecular_data.spinorb_from_spatial`, then pass
``0.5 * two_body_spin_orb`` into :class:`openfermion.InteractionOperator`.
"""

from __future__ import annotations

import numpy as np


def restore_packed_mo_eri_chemist(packed: np.ndarray, norb: int) -> np.ndarray:
    """Unpack PySCF ipack=4 MO ERIs to ``(norb, norb, norb, norb)`` without importing PySCF.

    Matches :func:`pyscf.ao2mo.restore` with ``symmetry=1`` for the common ``(npair, npair)``
    compact layout produced by CASCI ``get_h2eff`` and related exporters.
    """
    npair = norb * (norb + 1) // 2
    x = np.asarray(packed, dtype=float)
    if x.ndim == 4:
        if x.shape != (norb, norb, norb, norb):
            raise ValueError(f"unexpected dense h2 shape {x.shape}, expected ({norb},)*4")
        return x.copy()
    if x.ndim != 2 or x.shape != (npair, npair):
        raise ValueError(
            f"h2 packed array must have shape ({npair}, {npair}) for norb={norb}; got {x.shape}"
        )
    out = np.zeros((norb, norb, norb, norb), dtype=float)
    for i in range(norb):
        for j in range(i + 1):
            ij = i * (i + 1) // 2 + j
            for k in range(norb):
                for el in range(k + 1):
                    kl = k * (k + 1) // 2 + el
                    val = float(x[ij, kl])
                    out[i, j, k, el] = val
                    out[j, i, k, el] = val
                    out[i, j, el, k] = val
                    out[j, i, el, k] = val
    return out


def spatial_mo_eri_pyscf_to_openfermion_mo_ordering(h2_spatial: np.ndarray) -> np.ndarray:
    """Reorder spatial MO chemist ERIs from PySCF ``ao2mo``/CASCI layout to OpenFermion pairing.

    Args:
        h2_spatial: real 4-index array ``(norb, norb, norb, norb)`` from ``ao2mo.restore(1, ...)``
            or CASCI ``get_h2eff`` after restore.

    Returns:
        Transposed array suitable for :func:`openfermion.chem.molecular_data.spinorb_from_spatial`.
    """
    a = np.asarray(h2_spatial, dtype=float)
    if (
        a.ndim != 4
        or a.shape[0] != a.shape[1]
        or a.shape[0] != a.shape[2]
        or a.shape[0] != a.shape[3]
    ):
        raise ValueError("h2_spatial must be a real (norb, norb, norb, norb) array")
    return np.transpose(a, (0, 2, 3, 1))

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
    # Build index arrays for the upper-triangle packed pairs
    idx_i, idx_j = np.triu_indices(norb)
    # Map each (i,j) pair to its packed row index
    ij = idx_i * (idx_i + 1) // 2 + idx_j
    n_pairs = len(ij)

    # Fully vectorized: create all (ab, cd) combinations and use advanced indexing
    # ab_indices: [0, 0, 0, ..., 1, 1, 1, ..., n_pairs-1]  (length: n_pairs^2)
    # cd_indices: [0, 1, 2, ..., 0, 1, 2, ..., 0, 1, 2, ...]  (length: n_pairs^2)
    ab_indices = np.repeat(np.arange(n_pairs), n_pairs)
    cd_indices = np.tile(np.arange(n_pairs), n_pairs)

    # Extract all values from packed matrix at once
    values = x[ij[ab_indices], ij[cd_indices]]

    # Get the orbital indices for all combinations
    i_all = idx_i[ab_indices]
    j_all = idx_j[ab_indices]
    k_all = idx_i[cd_indices]
    l_all = idx_j[cd_indices]

    # Assign to all 4 symmetry copies using advanced indexing
    out[i_all, j_all, k_all, l_all] = values
    out[j_all, i_all, k_all, l_all] = values
    out[i_all, j_all, l_all, k_all] = values
    out[j_all, i_all, l_all, k_all] = values

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

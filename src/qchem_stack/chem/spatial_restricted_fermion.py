"""Build :class:`openfermion.FermionOperator` from restricted spatial MO integrals without a dense spin-orbital 4-index tensor."""

from __future__ import annotations

import numpy as np
from openfermion import FermionOperator
from openfermion.config import EQ_TOLERANCE


def restricted_spatial_integrals_to_fermion_operator(
    constant: float,
    h1: np.ndarray,
    h2_openfermion_ordered: np.ndarray,
    *,
    atol: float | None = None,
) -> FermionOperator:
    """Restricted closed-shell fermionic Hamiltonian in normal-ordered ladder operators.

    ``h2_openfermion_ordered`` must match OpenFermion MO layout (chemist ERIs after
    ``spatial_mo_eri_pyscf_to_openfermion_mo_ordering``). Coefficients match
    ``spinorb_from_spatial`` + ``InteractionOperator(..., 0.5 * h2_so)`` without
    allocating the ``(2*norb,)^4`` spin-orbital two-body array.

    Args:
        constant: Nuclear repulsion plus frozen-core shift (atomic units).
        h1: Spatial MO one-body matrix ``(norb, norb)``.
        h2_openfermion_ordered: Spatial MO ERIs ``(norb, norb, norb, norb)``.
        atol: Drop bilinear / quartic increments with ``abs(value) <= atol``.
            Defaults to OpenFermion :data:`~openfermion.config.EQ_TOLERANCE`.
    """
    if atol is None:
        atol = float(EQ_TOLERANCE)
    h1a = np.asarray(h1, dtype=float)
    h2a = np.asarray(h2_openfermion_ordered, dtype=float)
    norb = int(h1a.shape[0])
    if h1a.shape != (norb, norb):
        raise ValueError("h1 must be (norb, norb)")
    if h2a.shape != (norb, norb, norb, norb):
        raise ValueError("h2 must be (norb, norb, norb, norb)")

    # Build terms as dict to avoid slow incremental += (which is O(terms) per add)
    terms: dict[tuple, float] = {}

    # One-body terms - vectorized using numpy
    h1_mask = np.abs(h1a) > atol
    p_idx, q_idx = np.where(h1_mask)
    for p, q in zip(p_idx, q_idx, strict=False):
        c = float(h1a[p, q])
        terms[((int(2 * p), 1), (int(2 * q), 0))] = (
            terms.get(((int(2 * p), 1), (int(2 * q), 0)), 0.0) + c
        )
        terms[((int(2 * p + 1), 1), (int(2 * q + 1), 0))] = (
            terms.get(((int(2 * p + 1), 1), (int(2 * q + 1), 0)), 0.0) + c
        )

    # Two-body terms - vectorized: only iterate over non-zero elements
    h2_mask = np.abs(h2a) > atol
    nonzero_indices = np.argwhere(h2_mask)
    for p, q, r, s in nonzero_indices:
        p, q, r, s = int(p), int(q), int(r), int(s)
        coeff = 0.5 * float(h2a[p, q, r, s])
        # αααα
        t1 = ((2 * p, 1), (2 * q, 1), (2 * r, 0), (2 * s, 0))
        terms[t1] = terms.get(t1, 0.0) + coeff
        # ββββ
        t2 = ((2 * p + 1, 1), (2 * q + 1, 1), (2 * r + 1, 0), (2 * s + 1, 0))
        terms[t2] = terms.get(t2, 0.0) + coeff
        # αβαβ
        t3 = ((2 * p, 1), (2 * q + 1, 1), (2 * r + 1, 0), (2 * s, 0))
        terms[t3] = terms.get(t3, 0.0) + coeff
        # βαβα
        t4 = ((2 * p + 1, 1), (2 * q, 1), (2 * r, 0), (2 * s + 1, 0))
        terms[t4] = terms.get(t4, 0.0) + coeff

    # OpenFermion >=1.7 rejects dict bulk construction for multi-term ladders; build
    # term-by-term (still avoids O(n^2) SymbolicOperator += on growing dicts).
    fo = FermionOperator()
    for term_tuple, coeff in terms.items():
        fo += FermionOperator(term_tuple, coeff)
    if abs(float(constant)) > atol:
        fo += FermionOperator((), float(constant))
    return fo

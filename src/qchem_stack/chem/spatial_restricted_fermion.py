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

    fo = FermionOperator()
    fo += FermionOperator((), float(constant))

    for p in range(norb):
        for q in range(norb):
            c = float(h1a[p, q])
            if abs(c) <= atol:
                continue
            fo += FermionOperator(((2 * p, 1), (2 * q, 0)), c)
            fo += FermionOperator(((2 * p + 1, 1), (2 * q + 1, 0)), c)

    for p in range(norb):
        for q in range(norb):
            for r in range(norb):
                for s in range(norb):
                    v = float(h2a[p, q, r, s])
                    if abs(v) <= atol:
                        continue
                    coeff = 0.5 * v
                    fo += FermionOperator(((2 * p, 1), (2 * q, 1), (2 * r, 0), (2 * s, 0)), coeff)
                    fo += FermionOperator(
                        ((2 * p + 1, 1), (2 * q + 1, 1), (2 * r + 1, 0), (2 * s + 1, 0)),
                        coeff,
                    )
                    fo += FermionOperator(((2 * p, 1), (2 * q + 1, 1), (2 * r + 1, 0), (2 * s, 0)), coeff)
                    fo += FermionOperator(((2 * p + 1, 1), (2 * q, 1), (2 * r, 0), (2 * s + 1, 0)), coeff)
    return fo

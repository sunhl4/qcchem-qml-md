"""Jordan–Wigner mapping for :class:`openfermion.InteractionOperator` with optional coefficient cutoff."""

from __future__ import annotations

import itertools
from typing import cast

import numpy as np
from openfermion import InteractionOperator, jordan_wigner
from openfermion.ops import QubitOperator
from openfermion.transforms.opconversions.jordan_wigner import (
    jordan_wigner_one_body,
    jordan_wigner_two_body,
)
from openfermion.utils.operator_utils import count_qubits


def jordan_wigner_interaction_operator_sparse(
    iop: InteractionOperator,
    *,
    atol: float | None = None,
) -> QubitOperator:
    """JW transform mirroring OpenFermion ``_jordan_wigner_interaction_op`` with optional skips.

    When ``atol`` is ``None`` or ``<= 0``, delegates to :func:`openfermion.jordan_wigner`
    (byte-identical behaviour). When ``atol > 0``, skips accumulating Pauli shells whose
    combined coefficient magnitude does not exceed ``atol`` (fewer Python additions for
    nearly-zero tensor combinations).

    Same constraints as OpenFermion: expects a **real** Hermitian molecular-style operator.
    """
    if atol is None or float(atol) <= 0.0:
        return cast("QubitOperator", jordan_wigner(iop))

    eps = float(atol)
    n_qubits = count_qubits(iop)
    tb = np.asarray(iop.two_body_tensor)
    ob = np.asarray(iop.one_body_tensor)

    qubit_operator = QubitOperator((), float(iop.constant))

    for p in range(n_qubits):
        coefficient = complex(ob[p, p])
        if abs(coefficient) > eps:
            qubit_operator += jordan_wigner_one_body(p, p, coefficient)

    for p, q in itertools.combinations(range(n_qubits), 2):
        coefficient = 0.5 * (ob[p, q] + ob[q, p].conjugate())
        if abs(coefficient) > eps:
            qubit_operator += jordan_wigner_one_body(p, q, coefficient)

        coefficient = tb[p, q, p, q] - tb[p, q, q, p] - tb[q, p, p, q] + tb[q, p, q, p]
        if abs(coefficient) > eps:
            qubit_operator += jordan_wigner_two_body(p, q, p, q, coefficient)

    for (p, q), (r, s) in itertools.combinations(itertools.combinations(range(n_qubits), 2), 2):
        coefficient = 0.5 * (
            tb[p, q, r, s]
            + tb[s, r, q, p].conjugate()
            - tb[p, q, s, r]
            - tb[r, s, q, p].conjugate()
            - tb[q, p, r, s]
            - tb[s, r, p, q].conjugate()
            + tb[q, p, s, r]
            + tb[r, s, p, q].conjugate()
        )
        if abs(coefficient) > eps:
            qubit_operator += jordan_wigner_two_body(p, q, r, s, coefficient)

    return qubit_operator

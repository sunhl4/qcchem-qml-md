"""Pauli Hamiltonian dressing utilities for iterative QCC (iQCC)."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.quantum.algorithms.tolerances import NUMERICAL_TOLERANCE

if TYPE_CHECKING:
    from collections.abc import Iterable

__all__ = [
    "dress_by_pauli_rotation",
    "dress_product_unitary",
    "pauli_term_key",
    "reference_pauli_expectation",
    "truncate_qubit_operator",
]


def pauli_term_key(term: tuple[tuple[int, str], ...]) -> tuple[tuple[int, str], ...]:
    """Canonical sorted Pauli key."""
    return tuple(sorted(term, key=lambda x: x[0]))


def truncate_qubit_operator(
    op: QubitOperator,
    *,
    coeff_atol: float,
    max_terms: int | None = None,
) -> QubitOperator:
    """Drop tiny coefficients and optionally keep the largest ``max_terms`` magnitudes."""
    kept: list[tuple[tuple[tuple[int, str], ...], complex]] = []
    for term, coeff in op.terms.items():
        if abs(complex(coeff)) < float(coeff_atol):
            continue
        kept.append((term, complex(coeff)))
    if max_terms is not None and len(kept) > int(max_terms):
        kept.sort(key=lambda tc: abs(tc[1]), reverse=True)
        kept = kept[: int(max_terms)]
    out = QubitOperator()
    for term, coeff in kept:
        out += QubitOperator(term, coeff)
    return out


def dress_by_pauli_rotation(
    hamiltonian: QubitOperator,
    generator: QubitOperator,
    tau: float,
) -> QubitOperator:
    """Exact similarity transform ``U† H U`` for ``U = exp(-i τ P / 2)`` with Pauli ``P``.

    Closed form (``θ = τ/2``, ``P² = I``):

    $$
    H' = \\cos^2\\theta\\, H + \\sin^2\\theta\\, P H P
         + i\\sin\\theta\\cos\\theta\\, [P, H].
    $$
    """
    terms = list(generator.terms.items())
    if len(terms) != 1:
        raise ValueError("iQCC dressing requires a single-Pauli generator (one term).")
    term, coeff = terms[0]
    if abs(complex(coeff) - 1.0) > 1.0e-8 and abs(complex(coeff) + 1.0) > 1.0e-8:
        # Allow ±1; fold global phase into τ sign for +1 after normalization.
        phase = complex(coeff)
        if abs(abs(phase) - 1.0) > 1.0e-8:
            raise ValueError("Pauli generator coefficient must have unit magnitude.")
        tau = float(tau) * float(np.sign(phase.real) if abs(phase.imag) < 1e-12 else 1.0)
    p = QubitOperator(term, 1.0)
    theta = 0.5 * float(tau)
    c2 = math.cos(theta) ** 2
    s2 = math.sin(theta) ** 2
    sc = math.sin(theta) * math.cos(theta)
    php = p * hamiltonian * p
    comm = p * hamiltonian - hamiltonian * p
    dressed = c2 * hamiltonian + s2 * php + (1.0j * sc) * comm
    return dressed


def dress_product_unitary(
    hamiltonian: QubitOperator,
    generators: Iterable[QubitOperator],
    amplitudes: Iterable[float],
) -> QubitOperator:
    """Sequential dressing for ``U = ∏_k exp(-i τ_k P_k / 2)`` (left-to-right factor order)."""
    h = hamiltonian
    for gen, tau in zip(generators, amplitudes, strict=True):
        if abs(float(tau)) < NUMERICAL_TOLERANCE:
            continue
        h = dress_by_pauli_rotation(h, gen, float(tau))
    return h


def reference_pauli_expectation(
    hamiltonian: QubitOperator, reference: np.ndarray, n_qubits: int
) -> float:
    """``⟨ψ|H|ψ⟩`` for a dense reference statevector."""
    from qchem_stack.quantum.statevector import expectation_qubit_operator

    return float(np.real(expectation_qubit_operator(reference, hamiltonian, n_qubits)))

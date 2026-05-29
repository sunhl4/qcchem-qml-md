"""
Pauli support sets and strict ``evaluate``-compatibility checks.

Evaluate-stage protocols can reuse shot data only when a new observable lies in the
**measurement plan support** (see public docs on ``evaluate_expectation_value``). This
module implements a conservative **set-containment** criterion: every required Pauli string
must have been in the set measured (same canonical string encoding). It does *not* attempt
full symplectic linear-span analysis.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.pauli_term_codec import canonical_pauli_string_from_term

if TYPE_CHECKING:
    from openfermion.ops.operators.qubit_operator import QubitOperator

__all__ = [
    "assert_evaluate_compatible",
    "canonical_pauli_string_from_term",
    "hamiltonian_pauli_term_records",
    "pauli_string_set_from_qubit_operator",
    "pauli_strings_from_qubit_operator",
]


def hamiltonian_pauli_term_records(h: QubitOperator) -> list[dict[str, object]]:
    """
    Sorted non-identity Pauli terms with complex coefficients split for JSON export.

    Order is lexicographic on Pauli label (then real/imag) for stable Methods tables.
    """
    rows: list[dict[str, object]] = []
    for term, coeff in sorted(
        h.terms.items(),
        key=lambda tv: (
            canonical_pauli_string_from_term(tv[0]),
            complex(tv[1]).real,
            complex(tv[1]).imag,
        ),
    ):
        if term == ():
            continue
        c = complex(coeff)
        rows.append(
            {
                "pauli_string": canonical_pauli_string_from_term(term),
                "coefficient_real": float(c.real),
                "coefficient_imag": float(c.imag),
            }
        )
    return rows


def pauli_strings_from_qubit_operator(h: QubitOperator) -> tuple[str, ...]:
    """Sorted tuple of non-identity Pauli strings appearing in ``h``."""
    keys: list[str] = []
    for term in h.terms:
        if term == ():  # identity / constant — not in Pauli averaging support
            continue
        keys.append(canonical_pauli_string_from_term(term))
    return tuple(sorted(set(keys)))


def pauli_string_set_from_qubit_operator(h: QubitOperator) -> frozenset[str]:
    """Frozen set of non-identity Pauli strings in ``h`` (canonical encoding)."""
    return frozenset(pauli_strings_from_qubit_operator(h))


def assert_evaluate_compatible(measured_support: set[str], required_paulis: set[str]) -> None:
    """
    Raise ``ValueError`` if any ``required_paulis`` string was not in ``measured_support``.

    This encodes the strict "no free lunch" case from public evaluate-stage documentation:
    you cannot obtain an expectation for a Pauli that was never measured (in this
    conservative encoding).
    """
    missing = required_paulis - measured_support
    if missing:
        sample = sorted(missing)[:8]
        more = len(missing) - len(sample)
        suffix = f" (+{more} more)" if more > 0 else ""
        raise ValueError(
            "evaluate compatibility failed: required Pauli strings not in measured support: "
            f"{sample}{suffix}"
        )

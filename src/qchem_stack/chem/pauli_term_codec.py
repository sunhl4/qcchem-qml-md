"""Canonical encoding of OpenFermion Pauli term tuples (no ``protocols`` imports)."""

from __future__ import annotations


def canonical_pauli_string_from_term(term: tuple[tuple[int, str], ...]) -> str:
    """
    Stable string for an OpenFermion Pauli term (identity factors omitted).

    Empty tuple (identity) returns the literal ``\"I\"``.
    """
    if not term:
        return "I"
    parts = sorted(term, key=lambda t: t[0])
    return " ".join(f"{p}{idx}" for idx, p in parts)

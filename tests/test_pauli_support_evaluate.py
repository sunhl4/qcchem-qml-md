"""Pauli support encoding and evaluate compatibility."""

from __future__ import annotations

import pytest
from openfermion.ops import QubitOperator

from qchem_stack.protocols.pauli_support import (
    assert_evaluate_compatible,
    canonical_pauli_string_from_term,
    hamiltonian_pauli_term_records,
    pauli_string_set_from_qubit_operator,
    pauli_strings_from_qubit_operator,
)


def test_canonical_pauli_string_from_term() -> None:
    assert canonical_pauli_string_from_term(()) == "I"
    t = ((1, "Z"), (0, "X"))
    assert canonical_pauli_string_from_term(t) == "X0 Z1"


def test_pauli_strings_sorted_unique() -> None:
    q = QubitOperator("X0 Z1", 1.0) + QubitOperator("Z1 Z0", 0.5)
    s = pauli_strings_from_qubit_operator(q)
    assert len(s) == 2
    assert "X0 Z1" in s
    assert "Z0 Z1" in s


def test_assert_evaluate_compatible_ok() -> None:
    measured = {"X0 Z1", "Z0"}
    assert_evaluate_compatible(measured, {"X0 Z1"})


def test_assert_evaluate_compatible_raises() -> None:
    measured = {"X0 Z1"}
    with pytest.raises(ValueError, match="not in measured support"):
        assert_evaluate_compatible(measured, {"X0 Z1", "Y0"})


def test_pauli_string_set_from_qubit_operator() -> None:
    q = QubitOperator("Z0", 1.0)
    assert pauli_string_set_from_qubit_operator(q) == frozenset({"Z0"})


def test_hamiltonian_pauli_term_records_order() -> None:
    q = QubitOperator("Z1", 0.5) + QubitOperator("Z0", 0.25)
    rec = hamiltonian_pauli_term_records(q)
    assert [r["pauli_string"] for r in rec] == ["Z0", "Z1"]
    assert rec[0]["coefficient_real"] == pytest.approx(0.25)

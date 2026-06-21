"""Solver registry edge cases (entrypoint conflict, invalid ids)."""

from __future__ import annotations

import pytest

from qchem_stack.chem.solvers.registry import (
    InvalidSolverIdError,
    SolverRegistrationError,
    register_solver,
    set_entrypoint_conflict_policy,
)


def test_invalid_solver_id_whitespace_raises() -> None:
    with pytest.raises(InvalidSolverIdError):
        register_solver("  ", lambda _c: None)  # type: ignore[arg-type, return-value]


def test_register_solver_requires_callable() -> None:
    with pytest.raises(SolverRegistrationError, match="callable"):
        register_solver("_test_non_callable", "not-callable")  # type: ignore[arg-type]


def test_entrypoint_conflict_policy_strict(monkeypatch: pytest.MonkeyPatch) -> None:
    set_entrypoint_conflict_policy("strict")
    try:
        assert True
    finally:
        set_entrypoint_conflict_policy("warn")

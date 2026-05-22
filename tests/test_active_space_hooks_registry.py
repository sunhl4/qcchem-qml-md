"""Active-space hooks registry contract tests."""

from __future__ import annotations

import pytest

from qchem_stack.chem.active_space.hooks_registry import (
    get_active_space_hooks,
    list_active_space_hooks,
    register_active_space_hooks,
)
from qchem_stack.exceptions import PreQuantumCapabilityError


def test_active_space_hooks_registry_lists_builtins() -> None:
    tags = list_active_space_hooks()
    assert "pyscf" in tags
    assert "psi4" in tags


def test_active_space_hooks_registry_requires_explicit_override() -> None:
    hooks = get_active_space_hooks("pyscf")
    with pytest.raises(ValueError, match="already registered"):
        register_active_space_hooks("pyscf", hooks)


def test_active_space_hooks_registry_unknown_backend() -> None:
    with pytest.raises(PreQuantumCapabilityError, match="unknown-backend"):
        get_active_space_hooks("unknown-backend")

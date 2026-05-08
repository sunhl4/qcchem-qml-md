from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config import ActiveSpaceSpec


def test_active_space_cas_strategy_normalizes_to_legacy_fields() -> None:
    a = ActiveSpaceSpec(strategy="cas", ncas=4, nelecas=4)
    assert a.strategy == "cas"
    assert a.ncas == 4
    assert a.nelecas == 4
    assert a.n_active_orbitals == 4
    assert a.n_active_electrons == 4


def test_active_space_manual_strategy_accepts_frozen_orbitals() -> None:
    a = ActiveSpaceSpec(
        strategy="manual",
        n_active_orbitals=4,
        n_active_electrons=4,
        frozen_orbitals=[0, 1, 7],
    )
    assert a.strategy == "manual"
    assert a.n_active_orbitals == 4
    assert a.n_active_electrons == 4
    assert a.ncas == 4
    assert a.nelecas == 4
    assert a.frozen_orbitals == [0, 1, 7]


def test_active_space_manual_strategy_requires_legacy_sizes() -> None:
    with pytest.raises(ValidationError):
        ActiveSpaceSpec(strategy="manual", ncas=4, nelecas=4)


def test_active_space_cas_strategy_requires_cas_sizes() -> None:
    with pytest.raises(ValidationError):
        ActiveSpaceSpec(strategy="cas")


def test_active_space_manual_rejects_duplicate_frozen_orbitals() -> None:
    with pytest.raises(ValidationError):
        ActiveSpaceSpec(
            strategy="manual",
            n_active_orbitals=2,
            n_active_electrons=2,
            frozen_orbitals=[0, 0],
        )


def test_active_space_avas_stub_strategy_normalizes_like_cas() -> None:
    a = ActiveSpaceSpec(strategy="avas_stub", ncas=4, nelecas=4)
    assert a.strategy == "avas_stub"
    assert a.ncas == 4 and a.nelecas == 4
    assert a.n_active_orbitals == 4 and a.n_active_electrons == 4


def test_active_space_avas_strategy_normalizes_like_cas() -> None:
    a = ActiveSpaceSpec(strategy="avas", ncas=2, nelecas=2)
    assert a.strategy == "avas"
    assert a.ncas == 2 and a.nelecas == 2

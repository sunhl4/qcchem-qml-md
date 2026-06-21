from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config import ActiveSpaceSpec


def test_active_space_cas_strategy_normalizes_canonical_fields() -> None:
    a = ActiveSpaceSpec.model_validate(
        {"strategy": "cas", "cas": {"n_orbitals": 4, "n_electrons": 4}}
    )
    assert a.strategy == "cas"
    assert a.cas.n_orbitals == 4
    assert a.cas.n_electrons == 4


def test_active_space_cas_strategy_accepts_canonical_yaml_keys() -> None:
    a = ActiveSpaceSpec.model_validate(
        {
            "strategy": "cas",
            "cas": {"n_orbitals": 2, "n_electrons": 2},
            "mapping": {"fermion_qubit": "jordan_wigner"},
        }
    )
    assert a.cas.n_orbitals == 2
    assert a.mapping.fermion_qubit == "jordan_wigner"


def test_active_space_manual_strategy_accepts_frozen_orbitals() -> None:
    a = ActiveSpaceSpec.model_validate(
        {
            "strategy": "manual",
            "manual": {"n_orbitals": 4, "n_electrons": 4, "frozen_orbitals": [0, 1, 7]},
        }
    )
    assert a.strategy == "manual"
    assert a.cas.n_orbitals == 4
    assert a.cas.n_electrons == 4
    assert a.manual.frozen_orbitals == [0, 1, 7]


def test_active_space_manual_strategy_requires_sizes() -> None:
    with pytest.raises(ValidationError):
        ActiveSpaceSpec.model_validate({"strategy": "manual"})


def test_active_space_cas_strategy_requires_cas_sizes() -> None:
    with pytest.raises(ValidationError):
        ActiveSpaceSpec.model_validate({"strategy": "cas"})


def test_active_space_manual_rejects_duplicate_frozen_orbitals() -> None:
    with pytest.raises(ValidationError):
        ActiveSpaceSpec.model_validate(
            {
                "strategy": "manual",
                "manual": {
                    "n_orbitals": 2,
                    "n_electrons": 2,
                    "frozen_orbitals": [0, 0],
                },
            }
        )


def test_active_space_avas_stub_strategy_normalizes_like_cas() -> None:
    a = ActiveSpaceSpec.model_validate(
        {"strategy": "avas_stub", "cas": {"n_orbitals": 4, "n_electrons": 4}}
    )
    assert a.strategy == "avas_stub"
    assert a.cas.n_orbitals == 4 and a.cas.n_electrons == 4


def test_active_space_avas_strategy_normalizes_like_cas() -> None:
    a = ActiveSpaceSpec.model_validate(
        {"strategy": "avas", "cas": {"n_orbitals": 4, "n_electrons": 4}}
    )
    assert a.strategy == "avas"
    assert a.cas.n_orbitals == 4 and a.cas.n_electrons == 4

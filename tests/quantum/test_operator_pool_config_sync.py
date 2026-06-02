"""Operator pool registry ids stay aligned with config OperatorPoolId enum."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config import ExperimentConfig, OperatorPoolId, QuantumSpec
from qchem_stack.quantum.operator_pool_registry import (
    is_registered_operator_pool_id,
    list_registered_operator_pool_ids,
)
from tests.helpers.h2_yaml import h2_yaml_dict


def test_operator_pool_id_enum_values_are_registered() -> None:
    missing = [m.value for m in OperatorPoolId if not is_registered_operator_pool_id(m.value)]
    assert not missing, f"OperatorPoolId values missing from registry: {missing}"


def test_list_registered_includes_all_enum_values() -> None:
    registered = set(list_registered_operator_pool_ids())
    for member in OperatorPoolId:
        assert member.value in registered


def test_quantum_spec_rejects_unknown_pool_id_string() -> None:
    with pytest.raises(ValidationError):
        QuantumSpec.model_validate(
            {
                "algorithm": "adapt",
                "adapt": {"pool_id": "not_a_real_pool"},
            }
        )


def test_quantum_spec_accepts_alias_pool_id() -> None:
    spec = QuantumSpec.model_validate(
        {
            "algorithm": "iqeb",
            "iqeb": {"pool_id": OperatorPoolId.QUBIT_EXCITATION},
        }
    )
    assert spec.iqeb.pool_id == OperatorPoolId.QUBIT_EXCITATION


def test_experiment_config_roundtrip_with_canonical_pool_ids() -> None:
    cfg = ExperimentConfig.model_validate(
        h2_yaml_dict(
            molecule={"coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            quantum={
                "algorithm": "adapt",
                "adapt": {"pool_id": "fermionic_uccsd_singles"},
            },
        )
    )
    assert cfg.quantum.adapt.pool_id == OperatorPoolId.FERMIONIC_UCCSD_SINGLES

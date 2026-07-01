"""Tests for md_bridge energy reference consistency helpers."""

from __future__ import annotations

import warnings

import pytest

from qchem_stack.exceptions import ConfigurationError
from qchem_stack.md_bridge.energy_reference import (
    prepare_loop_config,
    resolved_validation_energy_reference,
    resolved_validation_theory_level,
    validate_loop_energy_consistency,
    warn_hf_forces_non_scf_energy,
)
from qchem_stack.md_bridge.md_loop_config import MdValidationLoopConfig


def test_resolved_validation_defaults() -> None:
    cfg = MdValidationLoopConfig()
    assert resolved_validation_energy_reference(cfg) == "variational"
    assert resolved_validation_theory_level(cfg) == "full_pipeline"


def test_resolved_validation_overrides() -> None:
    cfg = MdValidationLoopConfig(
        validation_energy_reference="scf",
        validation_theory_level="hf_scf",
    )
    assert resolved_validation_energy_reference(cfg) == "scf"
    assert resolved_validation_theory_level(cfg) == "hf_scf"


def test_warn_hf_forces_non_scf_energy() -> None:
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        warn_hf_forces_non_scf_energy(
            energy_reference="variational", include_hf_nuclear_gradient=True
        )
    assert any("inconsistent" in str(x.message).lower() for x in w)


def test_validate_loop_energy_consistency_strict_raises() -> None:
    cfg = MdValidationLoopConfig(
        validation_theory_level="hf_scf",
        validation_energy_reference="variational",
    )
    with pytest.raises(ConfigurationError):
        validate_loop_energy_consistency(cfg, strict=True)


def test_prepare_loop_config_returns_same_object() -> None:
    cfg = MdValidationLoopConfig()
    assert prepare_loop_config(cfg) is cfg

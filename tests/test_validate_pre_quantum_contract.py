"""Umbrella validate_pre_quantum_contract helper."""

from __future__ import annotations

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.config._experiment_validation import validate_pre_quantum_contract
from qchem_stack.exceptions import ConfigurationError
from tests.helpers.paths import configs_path


def test_validate_pre_quantum_contract_accepts_h2_pyscf() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    validate_pre_quantum_contract(cfg)


def test_validate_pre_quantum_contract_rejects_precomputed_with_benchmark() -> None:
    cfg = load_experiment_config(configs_path("example_h2_precomputed_bundle.yaml"))
    ce = cfg.chemistry_extended
    bad = cfg.model_copy(
        update={
            "chemistry_extended": ce.model_copy(
                update={
                    "benchmarks": ce.benchmarks.model_copy(update={"enabled": True}),
                }
            )
        }
    )
    with pytest.raises(ConfigurationError, match="precomputed"):
        validate_pre_quantum_contract(bad)

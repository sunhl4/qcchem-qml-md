"""Cross-field validation for scf.driver registration."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config import ExperimentConfig
from tests.helpers.h2_yaml import h2_yaml_dict


def _minimal_h2_raw(*, driver: str = "pyscf") -> dict[str, object]:
    return h2_yaml_dict(
        experiment_id="scf-driver-gate",
        molecule={"coordinates": [[0, 0, 0], [0, 0, 0.74]]},
        scf={"driver": driver, "method": "RHF"},
    )


def test_unknown_scf_driver_rejected_at_load() -> None:
    with pytest.raises(ValidationError, match="unknown_solver|Unknown scf.driver"):
        ExperimentConfig.model_validate(_minimal_h2_raw(driver="not_a_real_solver"))


def test_registered_scf_driver_loads() -> None:
    cfg = ExperimentConfig.model_validate(_minimal_h2_raw(driver="pyscf"))
    assert cfg.scf.driver == "pyscf"


def test_precomputed_driver_loads_when_registered() -> None:
    raw = _minimal_h2_raw(driver="precomputed")
    raw["scf"] = {
        "driver": "precomputed",
        "method": "RHF",
        "precomputed": {"bundle_path": "configs/precomputed_classical_reference_h2.json"},
    }
    cfg = ExperimentConfig.model_validate(raw)
    assert cfg.scf.driver == "precomputed"

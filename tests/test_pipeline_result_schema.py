from __future__ import annotations

import pytest

from qchem_stack.contracts.schema_ids import PIPELINE_RESULT_V1
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.orchestration.pipeline_result import (
    PIPELINE_RESULT_CORE_KEYS,
    assert_pipeline_result_core_keys,
    tag_pipeline_result,
)
from tests.helpers.paths import configs_path


def test_pipeline_result_core_keys_constant() -> None:
    assert "repro" in PIPELINE_RESULT_CORE_KEYS
    assert "scf_energy" in PIPELINE_RESULT_CORE_KEYS
    assert len(PIPELINE_RESULT_CORE_KEYS) == 8


def test_assert_pipeline_result_core_keys_raises() -> None:
    with pytest.raises(KeyError, match="missing core keys"):
        assert_pipeline_result_core_keys({})


def test_tag_pipeline_result_sets_schema() -> None:
    tagged = tag_pipeline_result({"scf_energy": -1.0})
    assert tagged["schema"] == PIPELINE_RESULT_V1


@pytest.mark.pyscf
def test_run_pipeline_sync_tags_pipeline_result_v1() -> None:
    pytest.importorskip("pyscf")
    cfg_path = configs_path("example_h2.yaml")
    from qchem_stack.config import load_experiment_config

    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert out["schema"] == PIPELINE_RESULT_V1
    assert_pipeline_result_core_keys(out)
    assert isinstance(out["repro"], dict)
    assert "run_summary" in out["repro"]
    assert out["pre_quantum_input"]["schema"] == "pre_quantum_input_v1"

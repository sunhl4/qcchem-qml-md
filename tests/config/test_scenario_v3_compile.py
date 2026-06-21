"""Scenario-first v3 compile and migration tests."""

from __future__ import annotations

import pytest

from qchem_stack.config import ExperimentConfig
from qchem_stack.config.migrations import migrate_config
from qchem_stack.config.migrations_v2_to_v3 import apply_dotted_set, compile_scenario_v3
from qchem_stack.config.scenarios import SCENARIOS, scenario_config_path


def test_compile_scenario_v3_minimal_vqe() -> None:
    raw = compile_scenario_v3(scenario_id="minimal_vqe")
    assert raw.get("scenario") == "minimal_vqe"
    assert raw.get("schema_version") == "3"
    cfg = ExperimentConfig.from_yaml_dict(migrate_config(raw))
    assert cfg.quantum is not None


@pytest.mark.parametrize("scenario_id", sorted(SCENARIOS))
def test_all_scenarios_compile_to_experiment_config(scenario_id: str) -> None:
    raw = compile_scenario_v3(scenario_id=scenario_id)
    assert raw.get("scenario") == scenario_id
    migrated = migrate_config(raw, from_version="3", to_version="2")
    cfg = ExperimentConfig.from_yaml_dict(migrated)
    assert cfg.quantum is not None or cfg.embedding is not None


def test_scenario_config_path_prefers_v3_stub() -> None:
    path = scenario_config_path("minimal_vqe")
    assert path.name == "minimal_vqe.yaml"
    assert "scenarios" in path.parts


def test_apply_dotted_set_overrides_nested_key() -> None:
    base = {"quantum": {"vqe": {"max_iter": 10}}}
    patched = apply_dotted_set(base, "quantum.vqe.max_iter=99")
    assert patched["quantum"]["vqe"]["max_iter"] == 99


def test_compile_scenario_v3_dotted_set_integration() -> None:
    raw = compile_scenario_v3(
        scenario_id="minimal_vqe",
        dotted_sets=["quantum.vqe.maxiter=77"],
    )
    migrated = migrate_config(raw, from_version="3", to_version="2")
    cfg = ExperimentConfig.from_yaml_dict(migrated)
    assert cfg.quantum is not None
    assert cfg.quantum.vqe.maxiter == 77


def test_migrate_v3_payload_to_v2() -> None:
    raw = {
        "schema_version": "3",
        "scenario": "minimal_vqe",
    }
    migrated = migrate_config(raw, from_version="3", to_version="2")
    assert migrated.get("schema_version") == "2"
    assert "scenario" not in migrated

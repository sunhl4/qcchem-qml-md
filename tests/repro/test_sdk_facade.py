"""SDK facade smoke tests."""

from __future__ import annotations

from tests.helpers.paths import configs_path


def test_sdk_export_parity_table_config_only() -> None:
    from qchem_stack.protocols import parity_criteria_export
    from qchem_stack.sdk import export_parity_table

    # Wheel-safe: no subprocess / repo scripts/ tree required.
    assert not hasattr(parity_criteria_export, "_repo_root")

    table = export_parity_table(configs_path("example_h2.yaml"))
    assert table.get("parity_export_schema_version") == "3"
    assert table.get("experiment_id")


def test_sdk_list_scenarios_includes_minimal_vqe() -> None:
    from qchem_stack.sdk import list_scenarios_text

    text = list_scenarios_text()
    assert "minimal_vqe" in text
    assert "configs/scenarios/minimal_vqe.yaml" in text


def test_sdk_workflow_preview_payload() -> None:
    from qchem_stack.sdk import load_experiment_config, workflow_preview_payload

    preview = workflow_preview_payload(load_experiment_config(configs_path("example_h2.yaml")))
    assert preview.get("schema") == "workflow_preview_v1"

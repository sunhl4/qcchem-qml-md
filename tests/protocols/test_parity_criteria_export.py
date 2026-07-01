"""Tests for in-package parity criteria export API."""

from __future__ import annotations

import json
from pathlib import Path

from tests.helpers.paths import configs_path


def test_export_parity_criteria_table_config_only_matches_cli() -> None:
    from qchem_stack.protocols.parity_criteria_export import export_parity_criteria_table
    from qchem_stack.protocols.parity_export_types import assert_stable_keys_present

    cfg = configs_path("example_h2.yaml")
    table = export_parity_criteria_table(cfg)
    assert table.get("parity_export_schema_version") == "3"
    assert_stable_keys_present(table)
    assert table.get("experiment_id")
    assert table.get("embedding", {}).get("mode") == "none"
    assert isinstance(table.get("capability_gap_categories"), list)


def test_sdk_export_without_repo_scripts() -> None:
    from qchem_stack.sdk import export_parity_table

    table = export_parity_table(configs_path("example_h2.yaml"))
    assert table.get("parity_export_schema_version") == "3"


def test_export_with_results_merge(tmp_path: Path) -> None:
    from qchem_stack.protocols.parity_criteria_export import export_parity_criteria_table

    results = {
        "scf_energy": -1.0,
        "protocol_counts": {
            "expectation_source": "executor_exact_or_device_mean",
            "hamiltonian_pauli_strings": ["II", "ZZ"],
        },
        "repro": {"run_summary": {"n_qubits": 4}},
    }
    results_path = tmp_path / "run.json"
    results_path.write_text(json.dumps(results), encoding="utf-8")
    table = export_parity_criteria_table(
        configs_path("example_h2.yaml"),
        results_path=results_path,
    )
    assert table.get("scf_energy_from_run") == -1.0
    assert table.get("protocol_expectation_source") == "executor_exact_or_device_mean"
    assert table.get("n_qubits_mirror_run_summary") == 4

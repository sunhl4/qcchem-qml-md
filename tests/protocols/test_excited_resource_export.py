"""Config-only excited resource export (protocols layer)."""

from __future__ import annotations

from qchem_stack.config import load_experiment_config
from qchem_stack.protocols.excited_resource_export import build_excited_resource_summary_for_export
from tests.helpers.paths import configs_path


def test_excited_resource_export_none_when_no_excited_stages() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    assert build_excited_resource_summary_for_export(cfg) is None


def test_excited_resource_export_vqd_block_from_yaml() -> None:
    cfg = load_experiment_config(configs_path("example_h2_vqd_uccsd.yaml"))
    block = build_excited_resource_summary_for_export(cfg)
    assert block is not None
    assert "vqd" in block
    assert block.get("excited_protocol_contract_v1", {}).get("schema")


def test_excited_resource_export_qse_sceom_bounds() -> None:
    cfg = load_experiment_config(configs_path("example_h2_uccsd_qse_pauli_qiskit.yaml"))
    block = build_excited_resource_summary_for_export(cfg)
    assert block is not None
    bounds = block.get("shot_channel_upper_bounds") or {}
    assert int(bounds.get("combined", 0)) >= 0

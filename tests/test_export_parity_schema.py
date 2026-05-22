"""Parity export schema fields (config-only export path)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.excited_stages import build_excited_resource_summary_for_export


def _load_export_script():
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "export_parity_criteria_table.py"
    spec = importlib.util.spec_from_file_location("export_parity_criteria_table", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_table_from_config_has_v3_fields() -> None:
    ep = _load_export_script()
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2.yaml"
    d = ep._table_from_config(p)
    assert d.get("parity_export_schema_version") == "3"
    assert d["computable_abstract"]["schema"] == "qchem_computable_abstract_v2"
    assert d["computable_abstract"].get("support_set_exported_from_protocol") is False
    assert "evaluate_note" in d["computable_abstract"]
    assert isinstance(d["capability_gap_categories"], list)
    assert d["embedding"]["mode"] == "none"


def test_excited_export_config_only_for_vqd_yaml() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_excited_smoke.yaml")
    block = build_excited_resource_summary_for_export(cfg)
    assert block is not None
    assert "excited_methods_unified" in block
    assert block.get("vqd") is not None or block.get("qse") is not None
    c = block.get("excited_protocol_contract_v1")
    assert isinstance(c, dict) and c.get("schema") == "excited_protocol_contract_v1"

"""Decomposition plugin embedding.mode==plugin (toy JSON Hamiltonian)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.chem.embedding.decomposition_plugin import (
    qubit_hamiltonian_from_decomposition_plugin,
)
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_decomposition_plugin_toy_yaml_runs() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_decomposition_plugin_toy.yaml"
    cfg = load_experiment_config(p)
    assert cfg.embedding.mode == "plugin"
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["hamiltonian_meta"].get("integral_source") == "decomposition_plugin_toy_v1"
    assert out["hamiltonian_meta"].get("integral_openfermion_bridge") == (
        "decomposition_plugin_pauli_terms_v1"
    )
    assert len(out["hamiltonian_meta"].get("hamiltonian_fingerprint", "")) == 32
    pre_q = out["pre_quantum_input"]
    assert pre_q.get("source") == "embedding_plugin"
    assert pre_q.get("integral_source") == "decomposition_plugin_toy_v1"
    assert pre_q.get("hamiltonian_summary", {}).get("hamiltonian_fingerprint")
    wf = out["embedding_workflow"]
    assert wf.get("mode") == "plugin"
    assert wf.get("decomposition_plugin") == "uniform_fragment_guess"
    assert wf.get("integral_source") == "decomposition_plugin_toy_v1"
    assert wf.get("decomposition_plugin_json_resolved_path")
    assert wf.get("epistemic_bound")
    assert "decomposition_plugin" in out["repro"]["run_summary"]["stages_completed"]


def test_decomposition_plugin_two_fragment_yaml_exposes_fragment_summary() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_decomposition_plugin_two_fragment.yaml"
    cfg = load_experiment_config(p)
    assert cfg.embedding.mode == "plugin"
    out = run_pipeline_sync(cfg, cfg_path=p)
    hm = out["hamiltonian_meta"]
    assert hm.get("decomposition_primary_fragment_id") == "f1"
    assert hm.get("decomposition_fragment_count") == 2
    assert hm.get("decomposition_fragment_ids") == ["f0", "f1"]
    assert hm.get("decomposition_fragment_pauli_term_counts") == {"f0": 4, "f1": 5}
    wf = out["embedding_workflow"]
    assert wf.get("decomposition_primary_fragment_id") == "f1"
    assert wf.get("decomposition_fragment_count") == 2
    assert wf.get("decomposition_fragment_ids") == ["f0", "f1"]
    assert wf.get("decomposition_fragment_pauli_term_counts") == {"f0": 4, "f1": 5}
    assert wf.get("decomposition_total_pauli_terms") == 9
    rs = out["repro"]["run_summary"]
    assert rs.get("decomposition_plugin_yaml") == "uniform_fragment_guess"
    assert rs.get("decomposition_primary_fragment_id") == "f1"
    assert rs.get("decomposition_fragment_count") == 2
    assert rs.get("decomposition_total_pauli_terms") == 9


def test_decomposition_plugin_contract_yaml_carries_fragment_energy_terms() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_decomposition_plugin_contract.yaml"
    cfg = load_experiment_config(p)
    assert cfg.embedding.mode == "plugin"
    out = run_pipeline_sync(cfg, cfg_path=p)
    hm = out["hamiltonian_meta"]
    assert hm.get("integral_source") == "decomposition_plugin_contract_v1"
    assert hm.get("decomposition_plugin_schema") == "decomposition_plugin_contract_v1"
    ledgers = hm.get("decomposition_fragment_energy_terms_v1")
    assert isinstance(ledgers, dict) and set(ledgers) >= {"f0", "f1"}
    assert ledgers["f0"].get("schema") == "fragment_energy_terms_stub_v1"
    wf = out["embedding_workflow"]
    assert wf.get("decomposition_plugin_schema") == "decomposition_plugin_contract_v1"
    assert isinstance(wf.get("decomposition_fragment_energy_terms_v1"), dict)


def test_decomposition_plugin_rejects_missing_primary_fragment(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_decomposition_plugin_toy.yaml"
    cfg = load_experiment_config(cfg_path)
    bad_payload = {
        "schema": "decomposition_plugin_toy_v1",
        "primary_fragment_id": "ghost",
        "fragments": {
            "f0": {
                "n_qubits": 2,
                "fermion_qubit_mapping": "jordan_wigner",
                "pauli_coefficients": [{"label": "II", "coeff": -0.5}],
            }
        },
    }
    bad_json = tmp_path / "bad_primary.json"
    bad_json.write_text(json.dumps(bad_payload), encoding="utf-8")
    cfg.embedding.decomposition_plugin_json_path = str(bad_json)
    with pytest.raises(ValueError, match="primary_fragment_id missing from fragments map"):
        _ = qubit_hamiltonian_from_decomposition_plugin(cfg, cfg_path=cfg_path)


def test_decomposition_plugin_rejects_invalid_secondary_fragment_pauli_shape(
    tmp_path: Path,
) -> None:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_decomposition_plugin_toy.yaml"
    cfg = load_experiment_config(cfg_path)
    bad_payload = {
        "schema": "decomposition_plugin_toy_v1",
        "primary_fragment_id": "f0",
        "fragments": {
            "f0": {
                "n_qubits": 2,
                "fermion_qubit_mapping": "jordan_wigner",
                "pauli_coefficients": [{"label": "II", "coeff": -0.5}],
            },
            "f1": {
                "n_qubits": 3,
                "fermion_qubit_mapping": "jordan_wigner",
                "pauli_coefficients": [{"label": "ZZ", "coeff": 0.1}],
            },
        },
    }
    bad_json = tmp_path / "bad_secondary_shape.json"
    bad_json.write_text(json.dumps(bad_payload), encoding="utf-8")
    cfg.embedding.decomposition_plugin_json_path = str(bad_json)
    with pytest.raises(ValueError, match="pauli label length 2 != n_qubits 3"):
        _ = qubit_hamiltonian_from_decomposition_plugin(cfg, cfg_path=cfg_path)

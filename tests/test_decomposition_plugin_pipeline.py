"""Decomposition plugin embedding.mode==plugin (toy JSON Hamiltonian)."""

from __future__ import annotations

from pathlib import Path

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_decomposition_plugin_toy_yaml_runs() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_decomposition_plugin_toy.yaml"
    cfg = load_experiment_config(p)
    assert cfg.embedding.mode == "plugin"
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["hamiltonian_meta"].get("integral_source") == "decomposition_plugin_toy_v1"
    wf = out["embedding_workflow"]
    assert wf.get("mode") == "plugin"
    assert wf.get("decomposition_plugin") == "uniform_fragment_guess"
    assert "decomposition_plugin" in out["repro"]["run_summary"]["stages_completed"]

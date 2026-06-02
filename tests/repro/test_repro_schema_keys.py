"""Smoke: pipeline repro keys align with repro.schema TypedDict coverage."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync

pytest.importorskip("pyscf")


def test_run_summary_and_protocol_counts_keys_present() -> None:
    cfg_path = Path("configs/example_h2.yaml")
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    repro = out.get("repro")
    assert isinstance(repro, dict)
    rsum = repro.get("run_summary")
    assert isinstance(rsum, dict)
    assert isinstance(rsum.get("stages_completed"), list)
    assert rsum.get("quantum_algorithm") is not None
    pc = out.get("protocol_counts")
    if isinstance(pc, dict) and pc:
        assert "expectation_source" in pc or "expectation" in pc
    rs = out.get("resource_summary")
    if isinstance(rs, dict) and rs.get("pauli_averaging_protocol_ran"):
        assert rs.get("n_circuits") is not None

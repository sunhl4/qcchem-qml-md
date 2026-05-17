"""Psi4 driver end-to-end pre-quantum path (optional dependency)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


@pytest.mark.psi4
def test_psi4_h2_pipeline_pre_quantum_summary() -> None:
    psi4 = pytest.importorskip("psi4")
    _ = psi4
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2_psi4_rhf_sto3g.yaml"
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    pqi = out["pre_quantum_input"]
    assert pqi["backend_tag"] == "psi4"
    assert pqi["source"] in ("canonical_active_space_integral_pack", "precomputed_bundle")
    assert pqi["hamiltonian_fingerprint"]

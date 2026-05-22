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


@pytest.mark.psi4
def test_psi4_schmidt_dmet_pipeline_summary() -> None:
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2_psi4_schmidt_dmet.yaml"
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    pqi = out["pre_quantum_input"]
    assert pqi["backend_tag"] == "psi4"
    assert pqi["source"] == "schmidt_atomic_production"
    assert pqi.get("hamiltonian_branch") == "schmidt_atomic_production"
    hm = out.get("hamiltonian_meta")
    assert isinstance(hm, dict)
    audit = hm.get("schmidt_production_audit")
    assert isinstance(audit, dict)
    ps = out["repro"].get("parity_snapshot", {})
    assert ps.get("dmet_solver_mode") == "schmidt_atomic_production"
    assert isinstance(ps.get("schmidt_embedding_production"), dict)


@pytest.mark.psi4
def test_psi4_projection_mulliken_pipeline_summary() -> None:
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2_psi4_projection_mulliken.yaml"
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    pqi = out["pre_quantum_input"]
    assert pqi["backend_tag"] == "psi4"
    assert pqi["source"] == "projection_fragment_mulliken_mo"
    assert pqi.get("hamiltonian_branch") == "projection_fragment_mulliken_mo"
    hm = out.get("hamiltonian_meta")
    assert isinstance(hm, dict)
    assert hm.get("integral_source") == "psi4_projection_fragment_mulliken_v1"

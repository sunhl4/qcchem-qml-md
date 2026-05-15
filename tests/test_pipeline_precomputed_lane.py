from __future__ import annotations

from pathlib import Path

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_pipeline_precomputed_bundle_lane_runs() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_precomputed_bundle.yaml")
    out = run_pipeline_sync(cfg, cfg_path=root / "configs" / "example_h2_precomputed_bundle.yaml")
    assert out["pre_quantum_input"]["schema"] == "pre_quantum_input_v1"
    assert out["pre_quantum_input"]["meta"]["source"] == "precomputed_bundle"
    assert out["hamiltonian_meta"]["integral_source"] == "classical_reference_bundle_v1"
    assert float(out["scf_energy"]) < 0.0

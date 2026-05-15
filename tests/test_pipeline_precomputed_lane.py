from __future__ import annotations

import json
from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_pipeline_precomputed_bundle_lane_runs() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_precomputed_bundle.yaml")
    out = run_pipeline_sync(cfg, cfg_path=root / "configs" / "example_h2_precomputed_bundle.yaml")
    assert out["pre_quantum_input"]["schema"] == "pre_quantum_input_v1"
    assert out["pre_quantum_input"]["meta"]["source"] == "precomputed_bundle"
    assert out["hamiltonian_meta"]["integral_source"] == "classical_reference_bundle_v1"
    assert float(out["scf_energy"]) < 0.0


def test_pipeline_precomputed_manifest_mismatch_fails_fast() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_precomputed_bundle.yaml"
    cfg = load_experiment_config(cfg_path)
    cfg_bad = cfg.model_copy(
        update={
            "active_space": cfg.active_space.model_copy(update={"n_active_orbitals": 3}),
        }
    )
    with pytest.raises(PipelineError, match="precomputed manifest mismatch: n_active_orbitals"):
        run_pipeline_sync(cfg_bad, cfg_path=cfg_path)


def test_pipeline_precomputed_manifest_fingerprint_mismatch_fails_fast(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    src_bundle = root / "configs" / "precomputed_classical_reference_h2.json"
    bundle = json.loads(src_bundle.read_text(encoding="utf-8"))
    bundle["manifest"] = dict(bundle.get("manifest") or {})
    bundle["manifest"]["schema"] = "precomputed_manifest_v1"
    bundle["manifest"]["config_fingerprint"] = "deadbeef"
    bad_bundle = tmp_path / "bad_bundle.json"
    bad_bundle.write_text(json.dumps(bundle), encoding="utf-8")
    cfg_path = root / "configs" / "example_h2_precomputed_bundle.yaml"
    cfg = load_experiment_config(cfg_path)
    cfg_bad = cfg.model_copy(
        update={
            "scf": cfg.scf.model_copy(update={"precomputed_bundle_path": str(bad_bundle)}),
        }
    )
    with pytest.raises(PipelineError, match="precomputed manifest mismatch: config_fingerprint"):
        run_pipeline_sync(cfg_bad, cfg_path=cfg_path)

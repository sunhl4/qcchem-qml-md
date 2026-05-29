from __future__ import annotations

import json
from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.helpers.paths import configs_path


def test_pipeline_precomputed_bundle_lane_runs() -> None:
    cfg = load_experiment_config(configs_path("example_h2_precomputed_bundle.yaml"))
    out = run_pipeline_sync(cfg, cfg_path=configs_path("example_h2_precomputed_bundle.yaml"))
    assert out["pre_quantum_input"]["schema"] == "pre_quantum_input_v1"
    assert out["pre_quantum_input"]["source"] == "precomputed_bundle"
    assert out["pre_quantum_input"]["integral_source"] == "classical_reference_bundle_v1"
    assert out["pre_quantum_input"]["fermion_to_qubit_map"] == "jordan_wigner"
    assert len(out["pre_quantum_input"]["hamiltonian_fingerprint"]) == 32
    assert out["pre_quantum_input"]["meta"]["source"] == "precomputed_bundle"
    assert out["hamiltonian_meta"]["integral_source"] == "classical_reference_bundle_v1"
    assert out["hamiltonian_meta"]["integral_openfermion_bridge"] == "precomputed_pauli_terms_v1"
    assert float(out["scf_energy"]) < 0.0
    ps = (out.get("repro") or {}).get("parity_snapshot") or {}
    exp_reg = ps.get("active_space_exporters_registry_v1") or {}
    assert exp_reg.get("schema") == "active_space_exporters_registry_v1"
    assert "pyscf" in (exp_reg.get("backend_tags") or [])
    branch_reg = ps.get("pre_quantum_branch_registry_v1") or {}
    assert branch_reg.get("schema") == "pre_quantum_branch_registry_v1"
    assert "precomputed_bundle" in (branch_reg.get("path_ids") or [])


def test_pipeline_precomputed_manifest_mismatch_fails_fast() -> None:
    cfg_path = configs_path("example_h2_precomputed_bundle.yaml")
    cfg = load_experiment_config(cfg_path)
    cfg_bad = cfg.model_copy(
        update={
            "active_space": cfg.active_space.model_copy(
                update={"cas": cfg.active_space.cas.model_copy(update={"n_orbitals": 3})}
            ),
        }
    )
    with pytest.raises(PipelineError, match="precomputed manifest mismatch: n_active_orbitals"):
        run_pipeline_sync(cfg_bad, cfg_path=cfg_path)


def test_pipeline_precomputed_manifest_fingerprint_mismatch_fails_fast(tmp_path: Path) -> None:
    src_bundle = configs_path("precomputed_classical_reference_h2.json")
    bundle = json.loads(src_bundle.read_text(encoding="utf-8"))
    bundle["manifest"] = dict(bundle.get("manifest") or {})
    bundle["manifest"]["schema"] = "precomputed_manifest_v1"
    bundle["manifest"]["config_fingerprint"] = "deadbeef"
    bad_bundle = tmp_path / "bad_bundle.json"
    bad_bundle.write_text(json.dumps(bundle), encoding="utf-8")
    cfg_path = configs_path("example_h2_precomputed_bundle.yaml")
    cfg = load_experiment_config(cfg_path)
    cfg_bad = cfg.model_copy(
        update={
            "scf": cfg.scf.model_copy(
                update={
                    "precomputed": cfg.scf.precomputed.model_copy(
                        update={"bundle_path": str(bad_bundle)}
                    )
                }
            ),
        }
    )
    with pytest.raises(PipelineError, match="precomputed manifest mismatch: config_fingerprint"):
        run_pipeline_sync(cfg_bad, cfg_path=cfg_path)


def test_pipeline_precomputed_manifest_missing_required_fields_fails_fast(tmp_path: Path) -> None:
    src_bundle = configs_path("precomputed_classical_reference_h2.json")
    bundle = json.loads(src_bundle.read_text(encoding="utf-8"))
    manifest = dict(bundle.get("manifest") or {})
    manifest.pop("n_qubits", None)
    bundle["manifest"] = manifest
    bad_bundle = tmp_path / "bad_bundle_missing_manifest_fields.json"
    bad_bundle.write_text(json.dumps(bundle), encoding="utf-8")
    cfg_path = configs_path("example_h2_precomputed_bundle.yaml")
    cfg = load_experiment_config(cfg_path)
    cfg_bad = cfg.model_copy(
        update={
            "scf": cfg.scf.model_copy(
                update={
                    "precomputed": cfg.scf.precomputed.model_copy(
                        update={"bundle_path": str(bad_bundle)}
                    )
                }
            ),
        }
    )
    with pytest.raises(PipelineError, match="precomputed manifest mismatch: required_fields"):
        run_pipeline_sync(cfg_bad, cfg_path=cfg_path)

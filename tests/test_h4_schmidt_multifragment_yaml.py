"""YAML-driven H4 Schmidt multifragment pipeline smoke."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.config._experiment_validation import validate_pre_quantum_contract
from qchem_stack.orchestration.pipeline import run_pipeline_sync


@pytest.mark.pyscf
@pytest.mark.slow
def test_h4_schmidt_multifragment_yaml_pipeline() -> None:
    pytest.importorskip("pyscf")
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h4_schmidt_multifragment.yaml"
    cfg = load_experiment_config(p)
    validate_pre_quantum_contract(cfg)
    out = run_pipeline_sync(cfg, cfg_path=p)
    assert out["pre_quantum_input"]["source"] == "schmidt_atomic_production"
    assert out["pre_quantum_input"]["hamiltonian_branch"] == "schmidt_atomic_production"
    assert out["pre_quantum_input"]["post_variational_embedding_audit_only"] is True
    ps = out["repro"]["parity_snapshot"]
    assert ps.get("schmidt_multifragment") is True
    assert ps.get("pre_quantum_handoff_v1", {}).get("source") == "schmidt_atomic_production"
    spfv = out.get("schmidt_per_fragment_vqe") or {}
    assert spfv.get("schema") == "schmidt_per_fragment_vqe_v1"
    assert len(spfv.get("fragments") or []) == 2

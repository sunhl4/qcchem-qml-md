"""DMET bath SCF self-consistency loop v1 with parity_snapshot trace."""

from __future__ import annotations

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")


def test_dmet_self_consistency_loop_converges_and_writes_parity_snapshot() -> None:
    p = configs_path("example_h4_dmet_self_consistent.yaml")
    if not p.is_file():
        pytest.skip("example_h4_dmet_self_consistent.yaml missing")
    cfg = load_experiment_config(p)
    assert cfg.embedding.n_scf_cycles_embedding is not None
    assert int(cfg.embedding.n_scf_cycles_embedding) >= 2
    out = run_pipeline_sync(cfg, cfg_path=p)
    loop = out.get("dmet_self_consistency_loop")
    assert isinstance(loop, dict)
    assert loop.get("schema") == "dmet_self_consistency_v1"
    assert loop.get("converged") is True
    assert int(loop.get("cycles") or 0) >= 2
    wf = out.get("embedding_workflow")
    assert isinstance(wf, dict)
    assert wf.get("dmet_self_consistency_loop_v1", {}).get("converged") is True
    snap = out["repro"]["parity_snapshot"]
    assert snap.get("n_scf_cycles_embedding") == cfg.embedding.n_scf_cycles_embedding
    traced = snap.get("dmet_self_consistency_loop")
    assert isinstance(traced, dict)
    assert traced.get("converged") is True
    assert int(traced.get("cycles") or 0) >= 2
    assert isinstance(traced.get("history"), list)

"""DMET multifragment shared-Hamiltonian exact fragment solver (optional slow)."""

from __future__ import annotations

from pathlib import Path

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


@pytest.mark.slow
def test_h4_dmet_multifragment_exact_shared_yaml() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h4_dmet_fragment_exact_small.yaml"
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    led = out["dmet_fragment_solve"]
    assert led.get("schema") == "dmet_one_shot_v1"
    assert led.get("multifragment_shared_global_hamiltonian") is True
    frags = led.get("fragments") or []
    assert len(frags) == 2
    def _frag_solver(f: dict) -> str | None:
        return f.get("solver") or (f.get("meta") or {}).get("solver")

    assert all(_frag_solver(f) == "QubitHamiltonianFragmentSolverExact" for f in frags)
    e0 = frags[0].get("energy")
    e1 = frags[1].get("energy")
    assert e0 is not None and e1 is not None
    assert float(e0) == pytest.approx(float(e1))

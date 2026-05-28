"""Psi4 solver integration smoke test (optional, requires psi4)."""

from __future__ import annotations

from pathlib import Path

import pytest

psi4 = pytest.importorskip("psi4")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.scf_stage import run_scf_reference


@pytest.mark.slow
@pytest.mark.psi4
def test_psi4_scf_reference_smoke() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_psi4_rhf_sto3g.yaml"
    if not cfg_path.is_file():
        pytest.skip("example_h2_psi4_rhf_sto3g.yaml missing")
    cfg = load_experiment_config(cfg_path)
    assert cfg.scf.driver == "psi4"
    out = run_scf_reference(cfg)
    assert out.e_tot < 0.0
    assert out.molecular_system is not None

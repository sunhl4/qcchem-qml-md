from __future__ import annotations

from pathlib import Path

from qchem_stack.chem.solvers import (
    create_solver,
    register_mock_external_solver,
    validate_solver_adapter_contract,
)
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_mock_external_solver_contract_check_passes() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    register_mock_external_solver()
    cfg.scf.driver = "mock_external"
    sol = create_solver(cfg)
    rep = validate_solver_adapter_contract(sol, run_mean_field=True)
    assert rep.ok
    assert rep.backend_id == "mock_external"


def test_mock_external_solver_runs_pipeline_plugin_path() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_decomposition_plugin_toy.yaml"
    cfg = load_experiment_config(cfg_path)
    register_mock_external_solver()
    cfg.scf.driver = "mock_external"
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert float(out["scf_energy"]) < 0.0
    assert (out.get("hamiltonian_meta") or {}).get("integral_source") == "decomposition_plugin_toy_v1"

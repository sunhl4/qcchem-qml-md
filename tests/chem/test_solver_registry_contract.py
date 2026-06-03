"""ChemIntegralSolver registry contract."""

from __future__ import annotations

from qchem_stack.chem.solvers import create_solver, register_mock_external_solver
from qchem_stack.chem.solvers.registry import registered_solver_ids
from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path


def test_builtin_solvers_registered() -> None:
    ids = registered_solver_ids()
    assert "pyscf" in ids
    assert "precomputed" in ids


def test_mock_external_after_register() -> None:
    register_mock_external_solver()
    assert "mock_external" in registered_solver_ids()
    cfg = load_experiment_config(configs_path("example_h2_mock_external.yaml"))
    solver = create_solver(cfg)
    assert solver.capabilities.backend_id == "mock_external"

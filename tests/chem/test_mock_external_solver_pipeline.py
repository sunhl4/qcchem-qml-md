"""Second registered classical backend (mock_external) interchange smoke."""

from __future__ import annotations

from qchem_stack.chem.solvers import create_solver, register_mock_external_solver
from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path


def test_mock_external_mean_field_deterministic() -> None:
    register_mock_external_solver()
    cfg = load_experiment_config(configs_path("example_h2_mock_external.yaml"))
    assert cfg.scf.driver == "mock_external"
    solver = create_solver(cfg)
    pack = solver.compute_mean_field()
    assert pack.e_tot < 0
    assert pack.driver_meta.get("classical_bridge_backend") == "mock_external"


def test_mock_external_capabilities_registry() -> None:
    register_mock_external_solver()
    cfg = load_experiment_config(configs_path("example_h2_mock_external.yaml"))
    caps = create_solver(cfg).capabilities
    assert caps.backend_id == "mock_external"
    assert caps.supports_molecular_scf is True
    assert caps.supports_restricted_active_space_qubit_hamiltonian is False

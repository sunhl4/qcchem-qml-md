"""Entry-point discovery for optional classical solvers."""

from __future__ import annotations

from qchem_stack.chem.solvers.registry import create_solver, registered_solver_ids
from tests.helpers.paths import configs_path


def test_mock_external_discovered_via_entry_point_group() -> None:
    from qchem_stack.config import load_experiment_config

    cfg = load_experiment_config(configs_path("example_h2_mock_external.yaml"))
    _ = create_solver(cfg)  # bootstrap discovers entry points
    assert "mock_external" in registered_solver_ids()

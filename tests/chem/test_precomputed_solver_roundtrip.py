"""PrecomputedIntegralSolver config validation and capability surface."""

from __future__ import annotations

import pytest

from qchem_stack.chem.solvers.precomputed_solver import PrecomputedIntegralSolver
from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path


def test_precomputed_solver_from_example_config() -> None:
    cfg = load_experiment_config(configs_path("example_h2_precomputed_bundle.yaml"))
    assert str(cfg.scf.driver).lower() == "precomputed"
    solver = PrecomputedIntegralSolver.from_experiment_config(cfg)
    assert solver.capabilities.backend_id == "precomputed"


def test_precomputed_solver_requires_bundle_path() -> None:
    cfg = load_experiment_config(configs_path("example_h2_precomputed_bundle.yaml"))
    cfg.scf.precomputed.bundle_path = ""
    with pytest.raises(ValueError, match="bundle_path"):
        PrecomputedIntegralSolver(cfg)

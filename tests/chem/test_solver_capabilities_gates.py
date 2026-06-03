"""Solver capability flags gate YAML paths without running heavy chemistry."""

from __future__ import annotations

import pytest

from qchem_stack.chem.integration.presets import capabilities_precomputed_offline
from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path


def test_precomputed_capabilities_offline_shape() -> None:
    caps = capabilities_precomputed_offline()
    assert caps.backend_id == "precomputed"
    assert caps.supports_molecular_scf is True
    assert caps.supports_restricted_active_space_qubit_hamiltonian is False
    assert caps.supports_pbc_scf is False


def test_precomputed_solver_rejects_non_precomputed_driver() -> None:
    from qchem_stack.chem.solvers.precomputed_solver import PrecomputedIntegralSolver

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    with pytest.raises(ValueError, match="precomputed"):
        PrecomputedIntegralSolver(cfg)


def test_custom_external_template_solver_registers() -> None:
    cfg = load_experiment_config(configs_path("example_custom_driver_template.yaml"))
    solver = create_solver(cfg)
    caps = solver.capabilities
    assert caps.backend_id == "custom_external_template"
    assert caps.supports_molecular_scf is False
    assert "supports_molecular_scf=True" in str(caps.capability_notes.get("molecular_scf", ""))

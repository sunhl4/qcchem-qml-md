"""Extra chem-layer coverage for adapter and bundle validation edges."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from qchem_stack.chem.precomputed_bundle import load_bundle_dict
from qchem_stack.chem.solvers import create_solver, register_mock_external_solver
from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path


def test_mock_external_periodic_raises() -> None:
    register_mock_external_solver()
    cfg = load_experiment_config(configs_path("example_h2_mock_external.yaml"))
    solver = create_solver(cfg)
    with pytest.raises(NotImplementedError, match="periodic"):
        solver.compute_mean_field(periodic=True)


def test_load_bundle_dict_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_bundle_dict("/nonexistent/precomputed_bundle.json")


def test_load_bundle_dict_invalid_schema_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps([]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_bundle_dict(str(bad))


def test_mock_external_solver_capabilities_registered() -> None:
    register_mock_external_solver()
    cfg = load_experiment_config(configs_path("example_h2_mock_external.yaml"))
    solver = create_solver(cfg)
    caps = solver.capabilities
    assert caps.supports_rhf is True


def test_projection_hamiltonian_module_importable() -> None:
    from qchem_stack.chem.embedding import projection_hamiltonian

    assert hasattr(projection_hamiltonian, "molecular_hamiltonian_fragment_mulliken_projection")

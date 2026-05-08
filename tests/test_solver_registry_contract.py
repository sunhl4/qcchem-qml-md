"""Registry bootstrap and :func:`~qchem_stack.chem.solvers.create_solver` wiring."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.chem.bridges.facade import classical_mean_field_via_solver_bridge
from qchem_stack.chem.solvers import create_solver, register_solver, registered_solver_ids
from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver
from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver
from qchem_stack.config import ExperimentConfig, load_experiment_config


def test_registered_solver_ids_include_pyscf_and_psi4() -> None:
    ids = registered_solver_ids()
    assert "pyscf" in ids
    assert "psi4" in ids


def test_register_solver_adds_custom_id() -> None:
    def _fake(_cfg: ExperimentConfig) -> PySCFIntegralSolver:
        raise RuntimeError("factory should not be invoked in this test")

    register_solver("_test_only_custom_solver", _fake)
    assert "_test_only_custom_solver" in registered_solver_ids()


def test_create_solver_pyscf_and_psi4(tmp_path: Path) -> None:
    cfg_path = tmp_path / "exp.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: reg_test
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    base = load_experiment_config(cfg_path)
    py = create_solver(base)
    assert isinstance(py, PySCFIntegralSolver)
    ps = create_solver(base.model_copy(update={"scf": base.scf.model_copy(update={"driver": "psi4"})}))
    assert isinstance(ps, Psi4IntegralSolver)


def test_example_h2_config_loads_through_registry_pyscf() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    sol = create_solver(cfg)
    assert isinstance(sol, PySCFIntegralSolver)


def test_classical_mean_field_facade_uses_registry_and_merges_headers(tmp_path: Path) -> None:
    """Downstream SCF entry must go through create_solver, not ad-hoc PySCF imports."""
    cfg_path = tmp_path / "exp.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: facade_registry
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    out = classical_mean_field_via_solver_bridge(cfg)
    assert out.driver_meta.get("upstream_classical_software_tag") == "pyscf"
    assert out.driver_meta.get("classical_problem_periodic_boundary_condition") is False
    assert float(out.e_tot) < 0.0


def test_psi4_compute_mean_field_smoke_and_canonical_headers(tmp_path: Path) -> None:
    pytest.importorskip("psi4")
    cfg_path = tmp_path / "exp_psi4.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: psi4_smoke
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: psi4
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    out = classical_mean_field_via_solver_bridge(cfg)
    assert out.driver_meta.get("upstream_classical_software_tag") == "psi4"
    assert out.driver_meta.get("classical_problem_periodic_boundary_condition") is False

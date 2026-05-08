"""M1 ChemIntegralSolver: Tangelo-oriented names (:meth:`compute_mean_field`, ``set_physical_data``, ``get_integrals``)."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.solvers import ChemIntegralSolver, create_solver
from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver
from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver
from qchem_stack.config import load_experiment_config

_EXAMPLE_H2 = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"


def test_pyscf_solver_is_protocol_member_and_compute_matches_run() -> None:
    cfg = load_experiment_config(_EXAMPLE_H2)
    sol = PySCFIntegralSolver.from_experiment_config(cfg)
    assert isinstance(sol, ChemIntegralSolver)
    a = sol.run_molecular_mean_field()
    b = sol.compute_mean_field(periodic=False)
    assert a.e_tot == pytest.approx(b.e_tot)


def test_pyscf_set_physical_data_rejects_non_pyscf_driver(tmp_path: Path) -> None:
    p = tmp_path / "c.yaml"
    p.write_text(
        """
schema_version: "1"
experiment_id: m1_gate
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
    bad_cfg = load_experiment_config(p)
    cfg = load_experiment_config(_EXAMPLE_H2)
    sol = PySCFIntegralSolver.from_experiment_config(cfg)
    with pytest.raises(ValueError, match="scf.driver='pyscf'"):
        sol.set_physical_data(bad_cfg)


def test_pyscf_get_integrals_stub_raises() -> None:
    cfg = load_experiment_config(_EXAMPLE_H2)
    sol = PySCFIntegralSolver.from_experiment_config(cfg)
    with pytest.raises(NotImplementedError, match="get_integrals"):
        sol.get_integrals()


def test_registry_create_solver_returns_tangelo_surface() -> None:
    cfg = load_experiment_config(_EXAMPLE_H2)
    sol = create_solver(cfg)
    assert hasattr(sol, "set_physical_data")
    assert hasattr(sol, "compute_mean_field")
    assert callable(sol.get_integrals)


def test_psi4_solver_set_physical_data_and_compute_aliases(tmp_path: Path) -> None:
    cfg_path = tmp_path / "psi4mini.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: m1_psi4
random_seed: 0
molecule:
  symbols: ["H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
  charge: 0
  multiplicity: 2
  basis: sto-3g
scf:
  driver: psi4
  method: RHF
active_space:
  n_active_orbitals: 1
  n_active_electrons: 1
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    s = Psi4IntegralSolver.from_experiment_config(cfg)
    assert isinstance(s, ChemIntegralSolver)
    cfg2_path = tmp_path / "pyscf_gate.yaml"
    cfg2_path.write_text(
        cfg_path.read_text(encoding="utf-8").replace("driver: psi4", "driver: pyscf"),
        encoding="utf-8",
    )
    cfg2 = load_experiment_config(cfg2_path)
    with pytest.raises(ValueError, match="scf.driver='psi4'"):
        s.set_physical_data(cfg2)
    try:
        out = s.compute_mean_field(periodic=False)
        assert out.driver_meta.get("driver_family") == "psi4"
    except RuntimeError as exc:
        assert "Psi4 SCF unavailable" in str(exc)
    with pytest.raises(NotImplementedError, match="PBC"):
        s.compute_mean_field(periodic=True)

"""Unit coverage for :class:`~qchem_stack.chem.solvers.pyscf_solver.PySCFIntegralSolver`."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ChemistryExtendedSpec, load_experiment_config


def _h2_system() -> MolecularSystem:
    return MolecularSystem(
        symbols=["H", "H"],
        coordinates_bohr=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]], dtype=float),
        charge=0,
        multiplicity=1,
        basis="sto-3g",
    )


def test_idle_molecular_driver_meta_matches_run_prefix() -> None:
    ext = ChemistryExtendedSpec()
    sol = PySCFIntegralSolver(_h2_system(), "RHF", ext)
    idle = sol.idle_molecular_driver_meta()
    assert idle["driver_family"] == "pyscf"
    assert idle["pbc"] is False
    assert idle["integral_representation"] == "mo"
    run = sol.run_molecular_mean_field()
    for k, v in idle.items():
        assert run.driver_meta.get(k) == v, k


def test_build_molecular_mf_without_kernel_returns_rhf_with_mol() -> None:
    sol = PySCFIntegralSolver(_h2_system(), "RHF", ChemistryExtendedSpec())
    mf = sol.build_molecular_mf_without_kernel()
    assert mf.mol.natm == 2


def test_pyscf_integral_solver_from_experiment_config(tmp_path: Path) -> None:
    cfg_path = tmp_path / "h2.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: adapter
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
  pyscf:
    init_guess: minao
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    sol = PySCFIntegralSolver.from_experiment_config(cfg)
    assert sol.init_guess == "minao"
    r = sol.run_molecular_mean_field()
    assert np.isfinite(r.e_tot)
    assert r.e_tot == pytest.approx(sol.compute_mean_field(periodic=False).e_tot)


def test_density_fit_wires_into_meta_and_mf() -> None:
    ext = ChemistryExtendedSpec()
    sol = PySCFIntegralSolver(
        _h2_system(),
        "RHF",
        ext,
        density_fit=True,
        density_fit_auxbasis="weigend",
    )
    mf = sol.build_molecular_mf_without_kernel()
    assert hasattr(mf, "with_df")
    run = sol.run_molecular_mean_field()
    assert run.driver_meta.get("scf_density_fit") is True
    assert run.driver_meta.get("scf_density_fit_auxbasis") == "weigend"


def test_get_integrals_returns_openfermion_reordered_tensor() -> None:
    sol = PySCFIntegralSolver(_h2_system(), "RHF", ChemistryExtendedSpec())
    out = sol.get_integrals(n_active_orbitals=2, n_active_electrons=2)
    assert out.get("schema") == "pyscf_active_space_integrals_v1"
    assert out.get("integral_representation") == "mo"
    assert out.get("openfermion_bridge") == "pyscf_spatial_openfermion_v1"
    h2_c = out.get("h2_spatial_mo_chemist")
    h2_of = out.get("h2_spatial_mo_openfermion")
    assert isinstance(h2_c, np.ndarray) and h2_c.shape == (2, 2, 2, 2)
    assert isinstance(h2_of, np.ndarray) and h2_of.shape == (2, 2, 2, 2)


def test_ecp_is_forwarded_to_pyscf_mol() -> None:
    sys = MolecularSystem(
        symbols=["Na"],
        coordinates_bohr=np.array([[0.0, 0.0, 0.0]], dtype=float),
        charge=0,
        multiplicity=2,
        basis="lanl2dz",
        ecp="lanl2dz",
    )
    sol = PySCFIntegralSolver(sys, "RHF", ChemistryExtendedSpec())
    mf = sol.build_molecular_mf_without_kernel()
    assert getattr(mf.mol, "ecp", None)


def test_zmatrix_config_path_runs_mean_field(tmp_path: Path) -> None:
    cfg_path = tmp_path / "h2_zmatrix.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: adapter_zmatrix
random_seed: 0
molecule:
  symbols: ["H", "H"]
  zmatrix: |
    H
    H 1 0.74
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    sol = PySCFIntegralSolver.from_experiment_config(cfg)
    out = sol.run_molecular_mean_field()
    assert np.isfinite(out.e_tot)

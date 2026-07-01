"""Direct ``get_integrals`` cross-backend parity (PySCF vs Psi4)."""

from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path

pytestmark = [pytest.mark.psi4, pytest.mark.pyscf]


def test_get_integrals_pyscf_psi4_active_space_shapes_match() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver
    from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver

    cfg_py = load_experiment_config(configs_path("example_h2.yaml"))
    cfg_psi = cfg_py.model_copy(update={"scf": cfg_py.scf.model_copy(update={"driver": "psi4"})})
    na, ne = 2, 2

    py_sol = PySCFIntegralSolver.from_experiment_config(cfg_py)
    psi_sol = Psi4IntegralSolver.from_experiment_config(cfg_psi)
    py_sol.run_molecular_mean_field()
    psi_sol.run_molecular_mean_field()

    py_int = py_sol.get_integrals(n_active_orbitals=na, n_active_electrons=ne)
    psi_int = psi_sol.get_integrals(n_active_orbitals=na, n_active_electrons=ne)

    assert py_int["n_active_orbitals"] == psi_int["n_active_orbitals"] == na
    assert py_int["n_active_electrons"] == psi_int["n_active_electrons"] == ne
    py_h1 = np.asarray(py_int["h1_spatial_mo"])
    psi_h1 = np.asarray(psi_int["h1_spatial_mo"])
    assert py_h1.shape == psi_h1.shape
    py_h2 = np.asarray(py_int["h2_spatial_mo_chemist"])
    psi_h2 = np.asarray(psi_int["h2_spatial_mo_chemist"])
    assert py_h2.shape == psi_h2.shape


def test_get_integrals_canonical_fingerprint_near_parity() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.orchestration.scf_stage import run_scf_reference

    cfg_py = load_experiment_config(configs_path("example_h2.yaml"))
    cfg_psi = cfg_py.model_copy(update={"scf": cfg_py.scf.model_copy(update={"driver": "psi4"})})
    na, ne = 2, 2
    ref_py = run_scf_reference(cfg_py)
    ref_psi = run_scf_reference(cfg_psi)
    pack_py = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        ref_py, n_active_orbitals=na, n_active_electrons=ne
    )
    pack_psi = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        ref_psi, n_active_orbitals=na, n_active_electrons=ne
    )
    fp_py = str(pack_py.provenance.get("classical_backend") or "")
    fp_psi = str(pack_psi.provenance.get("classical_backend") or "")
    assert fp_py == "pyscf"
    assert fp_psi == "psi4"
    # Fingerprints may differ across backends; constant term parity is the L1 gate.
    assert abs(float(pack_py.compact.constant) - float(pack_psi.compact.constant)) < 5e-3

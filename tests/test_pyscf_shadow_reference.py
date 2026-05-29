from __future__ import annotations

import numpy as np
import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")
from qchem_stack.chem.bridges.casci_core_count import casci_ncore_spatial
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.bridges.pyscf_shadow_reference import build_pyscf_rhf_shadow
from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver
from qchem_stack.config import load_experiment_config


def test_pyscf_shadow_imports_mo_without_rescf() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    solver = PySCFIntegralSolver.from_experiment_config(cfg)
    run = solver.run_molecular_mean_field()
    ref = ClassicalMeanFieldReference(
        mf=run.mf,
        e_tot=float(run.e_tot),
        mo_energy=run.mo_energy,
        molecular_system=cfg.molecule,
        driver_meta={**dict(run.driver_meta), "upstream_classical_software_tag": "pyscf"},
    )
    mo_native = np.asarray(ref.mf.mo_coeff, dtype=float)
    shadow = build_pyscf_rhf_shadow(cfg, ref, run_scf_if_needed=False)
    assert np.allclose(shadow.mo_coeff, mo_native, atol=1e-10)
    assert shadow.converged
    assert not hasattr(shadow, "_scf_called")


def test_casci_ncore_matches_even_electron_heuristic() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    ncore = casci_ncore_spatial(cfg, n_mo=4, n_active_electrons=2, n_active_orbitals=2)
    assert ncore == 0

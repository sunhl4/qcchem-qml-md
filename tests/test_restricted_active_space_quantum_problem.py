"""Restricted active-space quantum problem (InQuanto ``get_system`` analog)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.config import load_experiment_config
from qchem_stack.tensornet.dense_expectation_reference import expectation_qubit_operator_dense


def test_restricted_active_space_problem_matches_pipeline_geometry() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    prob = drv.get_restricted_active_space_quantum_problem(
        2, 2, fermion_qubit_mapping="jordan_wigner"
    )
    assert prob.compact_mo_operator.storage_schema == "pyscf_casci_h2eff_compact_v1"
    assert prob.compact_mo_operator.n_active_orbitals == 2
    assert prob.fermion_space.n_electrons == 2
    assert prob.fermion_space.n_spin_orbitals == 4
    assert prob.hartree_fock_state_jw.shape == (16,)
    assert prob.qubit_hamiltonian.n_qubits == 4
    assert prob.meta.get("schema") == "restricted_active_space_quantum_problem_v1"
    e = expectation_qubit_operator_dense(
        prob.qubit_hamiltonian.operator,
        prob.hartree_fock_state_jw,
        n_qubits=4,
    )
    assert np.isfinite(float(np.real(e)))


def test_get_system_ao_marks_integral_representation() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    ao = drv.get_system_ao(run_hf=True)
    assert ao.driver_meta.get("integral_representation") == "ao"
    assert ao.driver_meta.get("ao_reference_kind") == "scf_object"
    assert ao.e_tot is not None


def test_pyscf_symmetry_configuration_surfaces_in_problem_meta() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    cx = cfg.chemistry_extended.model_copy(update={"pyscf_symmetry": True})
    cfg2 = cfg.model_copy(update={"chemistry_extended": cx})
    drv = PySCFDriver.from_config(cfg2)
    prob = drv.get_restricted_active_space_quantum_problem(2, 2)
    assert "pyscf_symmetry_detected" in prob.meta


def test_restricted_active_space_problem_rejects_uhf_reference() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    scf = cfg.scf.model_copy(update={"method": "UHF"})
    cfg2 = cfg.model_copy(update={"scf": scf})
    drv = PySCFDriver.from_config(cfg2)
    with pytest.raises(ValueError, match="RHF references only"):
        drv.get_restricted_active_space_quantum_problem(2, 2)

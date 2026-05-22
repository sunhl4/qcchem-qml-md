"""Tests for bridge-layer quantum problem and PySCF system factories."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.molecular_problem_build import (
    restricted_active_space_quantum_problem_from_config,
)
from qchem_stack.chem.systems.pyscf_factory import (
    pyscf_ao_system_from_config,
    pyscf_ao_system_without_scf,
)
from qchem_stack.config import load_experiment_config
from qchem_stack.tensornet.dense_expectation_reference import expectation_qubit_operator_dense


def test_restricted_active_space_quantum_problem_from_config() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    prob = restricted_active_space_quantum_problem_from_config(cfg)
    assert prob.compact_mo_operator.n_active_orbitals == 2
    assert prob.qubit_hamiltonian.n_qubits == 4
    e = expectation_qubit_operator_dense(
        prob.qubit_hamiltonian.operator,
        prob.hartree_fock_state_jw,
        n_qubits=4,
    )
    assert np.isfinite(float(np.real(e)))


def test_pyscf_ao_system_from_config() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    ao = pyscf_ao_system_from_config(cfg, run_hf=True)
    assert ao.driver_meta.get("integral_representation") == "ao"
    assert ao.e_tot is not None


def test_pyscf_ao_system_without_scf() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    ao = pyscf_ao_system_without_scf(cfg)
    assert ao.driver_meta.get("ao_run_hf") is False
    assert ao.e_tot is None

"""Restricted active-space quantum problem (PySCF ``get_system`` analog)."""

from __future__ import annotations

import numpy as np
import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")

from qchem_stack.chem.molecular_problem_build import (
    restricted_active_space_quantum_problem_from_config,
)
from qchem_stack.chem.systems.pyscf_factory import pyscf_ao_system_from_config
from qchem_stack.config import load_experiment_config
from qchem_stack.tensornet.dense_expectation_reference import expectation_qubit_operator_dense


def test_restricted_active_space_problem_matches_pipeline_geometry() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    prob = restricted_active_space_quantum_problem_from_config(
        cfg,
        fermion_qubit_mapping="jordan_wigner",
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
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    ao = pyscf_ao_system_from_config(cfg, run_hf=True)
    assert ao.driver_meta.get("integral_representation") == "ao"
    assert ao.driver_meta.get("ao_reference_kind") == "scf_object"
    assert ao.e_tot is not None


def test_pyscf_symmetry_configuration_surfaces_in_problem_meta() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    cx = cfg.chemistry_extended.model_copy(update={"pyscf_symmetry": True})
    cfg2 = cfg.model_copy(update={"chemistry_extended": cx})
    prob = restricted_active_space_quantum_problem_from_config(cfg2)
    assert "pyscf_symmetry_detected" in prob.meta


def test_restricted_active_space_problem_rejects_uhf_reference() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    scf = cfg.scf.model_copy(update={"method": "UHF"})
    cfg2 = cfg.model_copy(update={"scf": scf})
    with pytest.raises(ValueError, match="RHF references only"):
        restricted_active_space_quantum_problem_from_config(cfg2)

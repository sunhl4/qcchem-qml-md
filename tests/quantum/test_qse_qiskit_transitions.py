from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pyscf")
pytest.importorskip("qiskit")

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.quantum.algorithms.excited import QSE
from qchem_stack.quantum.variational_branch import build_uccsd_variational_model
from tests.helpers.paths import configs_path
from tests.test_gap_closure_and_ucc import pyscf_rhf_from_config


def test_qse_uccsd_qiskit_transitions_smoke() -> None:
    cfg = load_experiment_config(configs_path("example_h2_uccsd.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    qh = build_pre_quantum_input(cfg, ref).hamiltonian
    exe = StatevectorHeaExecutor()
    model = build_uccsd_variational_model(qh, exe, trotter_steps=None)
    angles = np.linspace(-0.05, 0.05, model.n_params)
    qse = QSE(qh, subspace_dim=4)
    exact = qse.run_from_uccsd_basis(angles, model.prepare_state, max_basis=4)
    qiskit = qse.run_from_uccsd_basis_pauli_transitions_qiskit(
        angles,
        model.prepare_state,
        max_basis=4,
        shots_per_ij_term=2048,
    )
    assert qiskit.meta["shot_noise_model"] == "qiskit_histogram_per_ij_term"
    if exact.excitation_energies and qiskit.excitation_energies:
        assert abs(exact.excitation_energies[0] - qiskit.excitation_energies[0]) < 0.8

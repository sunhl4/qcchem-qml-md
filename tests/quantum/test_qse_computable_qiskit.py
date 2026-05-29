"""QSEMatricesComputable qiskit shot_mode alignment."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pyscf")
pytest.importorskip("qiskit")

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.protocols.computables.base import EvaluationContext
from qchem_stack.protocols.computables.qse_matrices import QSEMatricesComputable
from qchem_stack.quantum.algorithms.excited import QSE
from qchem_stack.quantum.algorithms.excited_basis import build_qse_basis_from_uccsd_reference
from qchem_stack.quantum.variational_branch import build_uccsd_variational_model
from tests.helpers.paths import configs_path
from tests.test_gap_closure_and_ucc import pyscf_rhf_from_config


def test_qse_matrices_computable_qiskit_uccsd_path() -> None:
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
    angles = np.zeros(model.n_params, dtype=float)
    basis = build_qse_basis_from_uccsd_reference(
        angles, qh, model.prepare_state, max_basis=3, expansion_pool="fermionic_singles"
    )
    comp = QSEMatricesComputable(
        "qse_h_s",
        qh.operator,
        qh.n_qubits,
        basis=basis,
        shot_mode="pauli_transitions_qiskit",
        shots_per_ij_term=1024,
    )
    comp_out = comp.evaluate(EvaluationContext(angles=np.zeros(0)))
    direct = QSE(qh, subspace_dim=4).run_from_uccsd_basis_pauli_transitions_qiskit(
        angles, model.prepare_state, max_basis=3, shots_per_ij_term=1024
    )
    assert comp_out.meta.get("computable_runtime") == "QSEMatricesComputable"
    assert comp_out.meta.get("shot_noise_model") == "qiskit_histogram_per_ij_term"
    assert np.asarray(comp_out.value["H"]).shape[0] == len(basis)
    assert direct.meta.get("computable_runtime") == "QSEMatricesComputable"
    assert len(direct.excitation_energies) >= 1

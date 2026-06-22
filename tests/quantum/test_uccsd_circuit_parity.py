from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.backends.uccsd_circuit_qiskit import statevector_from_circuit_ir
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.quantum.algorithms.uccsd_circuit import (
    UCCSDCircuitContext,
    uccsd_circuit_ir,
    uccsd_prepare_statevector,
)
from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE
from tests.fixtures.classical_reference import pyscf_rhf_from_config
from tests.helpers.paths import configs_path


def _h2_qh():
    cfg = load_experiment_config(configs_path("example_h2_uccsd.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    return build_pre_quantum_input(cfg, ref).hamiltonian


def test_uccsd_circuit_statevector_matches_dense_prepare_state() -> None:
    qh = _h2_qh()
    exe = StatevectorHeaExecutor()
    ucc = UCCSDVQE(qh, executor=exe)
    ctx = UCCSDCircuitContext.from_hamiltonian(qh, trotter_steps=None)
    angles = np.linspace(-0.2, 0.3, ucc.n_params)
    psi_dense = ucc.prepare_state(angles)
    psi_circuit = uccsd_prepare_statevector(angles, ctx, n_qubits=qh.n_qubits)
    assert float(np.linalg.norm(psi_dense - psi_circuit)) < 1e-8


def test_uccsd_circuit_qiskit_statevector_parity() -> None:
    qh = _h2_qh()
    ctx = UCCSDCircuitContext.from_hamiltonian(qh, trotter_steps=None)
    angles = np.linspace(-0.15, 0.25, len(ctx.antiherm_mats))
    psi_ref = uccsd_prepare_statevector(angles, ctx, n_qubits=qh.n_qubits)
    psi_qiskit = statevector_from_circuit_ir(uccsd_circuit_ir(angles, ctx, n_qubits=qh.n_qubits))
    assert float(np.linalg.norm(psi_ref - psi_qiskit)) < 1e-6


def test_uccsd_trotter_circuit_matches_trotter_vqe_prepare_state() -> None:
    qh = _h2_qh()
    exe = StatevectorHeaExecutor()
    ucc = UCCSDTrotterVQE(qh, executor=exe, n_trotter_steps=2)
    ctx = UCCSDCircuitContext.from_hamiltonian(qh, trotter_steps=2)
    angles = np.linspace(-0.1, 0.2, ucc.n_params)
    psi_dense = ucc.prepare_state(angles)
    psi_circuit = uccsd_prepare_statevector(angles, ctx, n_qubits=qh.n_qubits)
    assert float(np.linalg.norm(psi_dense - psi_circuit)) < 1e-8

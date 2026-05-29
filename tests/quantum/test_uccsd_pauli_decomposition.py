from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.backends.spec import BackendSpec, circuit_resource_row
from qchem_stack.backends.uccsd_circuit_qiskit import statevector_from_circuit_ir
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.quantum.algorithms.uccsd_circuit import (
    UCCSDCircuitContext,
    uccsd_circuit_ir,
    uccsd_prepare_statevector,
)
from qchem_stack.quantum.algorithms.uccsd_pauli_decomposition import (
    cluster_expm_via_pauli_product,
    decompose_antihermitian_to_pauli_terms,
)
from tests.helpers.paths import configs_path
from tests.test_gap_closure_and_ucc import pyscf_rhf_from_config


def _qh_from_config(rel: str):
    cfg = load_experiment_config(configs_path(rel))
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    return build_pre_quantum_input(cfg, ref).hamiltonian


def test_pauli_cluster_product_matches_expm_h2() -> None:
    qh = _qh_from_config("example_h2_uccsd.yaml")
    ctx = UCCSDCircuitContext.from_hamiltonian(qh, trotter_steps=None)
    angles = np.linspace(-0.2, 0.35, len(ctx.antiherm_mats))
    psi_ref = uccsd_prepare_statevector(angles, ctx, n_qubits=qh.n_qubits)
    ir = uccsd_circuit_ir(angles, ctx, n_qubits=qh.n_qubits, decomposition_mode="pauli")
    psi_qiskit = statevector_from_circuit_ir(ir)
    assert float(np.linalg.norm(psi_ref - psi_qiskit)) < 1e-6
    assert any(op["name"] in {"CX", "RZ", "H", "X", "SX"} for op in ir.operations)


def test_pauli_decomposition_terms_nontrivial_h2() -> None:
    qh = _qh_from_config("example_h2_uccsd.yaml")
    ctx = UCCSDCircuitContext.from_hamiltonian(qh, trotter_steps=None)
    terms = decompose_antihermitian_to_pauli_terms(ctx.antiherm_mats[0], qh.n_qubits)
    assert len(terms) >= 2
    u = cluster_expm_via_pauli_product(ctx.antiherm_mats[0], 0.25, qh.n_qubits)
    assert u.shape == (2**qh.n_qubits, 2**qh.n_qubits)


def test_pauli_circuit_resource_row_has_twoq_h2() -> None:
    qh = _qh_from_config("example_h2_uccsd.yaml")
    ctx = UCCSDCircuitContext.from_hamiltonian(qh, trotter_steps=None)
    angles = np.linspace(-0.12, 0.18, len(ctx.antiherm_mats))
    ir = uccsd_circuit_ir(angles, ctx, n_qubits=qh.n_qubits, decomposition_mode="pauli")
    row = circuit_resource_row("uccsd_pauli", ir, shots=1024, backend=BackendSpec(name="sv"))
    assert int(row["twoq_count"]) > 0
    assert int(row["depth"]) > 0


@pytest.mark.slow
def test_pauli_circuit_parity_h4_active_space() -> None:
    qh = _qh_from_config("example_h4_dmet_fragment_exact_small.yaml")
    if qh.n_qubits > 8:
        pytest.skip("H4 parity skipped for large active spaces")
    ctx = UCCSDCircuitContext.from_hamiltonian(qh, trotter_steps=None)
    if len(ctx.antiherm_mats) == 0:
        pytest.skip("no UCCSD generators")
    angles = np.linspace(-0.05, 0.05, len(ctx.antiherm_mats))
    psi_ref = uccsd_prepare_statevector(angles, ctx, n_qubits=qh.n_qubits)
    ir = uccsd_circuit_ir(angles, ctx, n_qubits=qh.n_qubits, decomposition_mode="pauli")
    psi_qiskit = statevector_from_circuit_ir(ir)
    assert float(np.linalg.norm(psi_ref - psi_qiskit)) < 1e-5

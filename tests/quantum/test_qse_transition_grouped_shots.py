from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.qse_transition import (
    estimate_transition_pauli_amplitude_grouped_shots,
    qse_h_matrix_transition_grouped_pauli_shots,
    transition_pauli_amplitude,
)

pytestmark = pytest.mark.l1_excited


def _toy_h() -> QubitHamiltonian:
    op = QubitOperator(((0, "Z"),), 0.4) + QubitOperator(((1, "X"),), 0.2) + QubitOperator((), 0.05)
    return QubitHamiltonian(operator=op, n_qubits=2, fermion_space=FermionSpace(2, 1))


def test_grouped_transition_amp_converges_to_exact_with_many_shots() -> None:
    phi_a = np.array([1.0, 0.1, 0.2, 0.0], dtype=complex)
    phi_b = np.array([0.9, 0.2, 0.1, 0.05], dtype=complex)
    phi_a /= np.linalg.norm(phi_a)
    phi_b /= np.linalg.norm(phi_b)
    term = ((0, "Z"),)
    exact = transition_pauli_amplitude(phi_a, phi_b, term, 2)
    est = estimate_transition_pauli_amplitude_grouped_shots(
        phi_a, phi_b, term, 2, shots=8000, rng=np.random.default_rng(0)
    )
    assert abs(est - exact) < 0.05 * max(1.0, abs(exact))


def test_qse_grouped_pauli_shots_produces_finite_excitation_block() -> None:
    qh = _toy_h()
    basis = [np.array([1, 0, 0, 0], dtype=complex), np.array([0, 1, 0, 0], dtype=complex)]
    h_sym, s_mat, records = qse_h_matrix_transition_grouped_pauli_shots(
        basis,
        qh.operator,
        qh.n_qubits,
        shots_per_ij_term=256,
        rng=np.random.default_rng(1),
    )
    assert h_sym.shape == (2, 2)
    assert s_mat.shape == (2, 2)
    assert records
    assert records[0]["noise_model"] == "grouped_statevector_shot_simulation_per_ij_term"
    assert np.all(np.isfinite(np.real(h_sym)))

"""SCBK mapping edge cases (qubit count reduction, validation)."""

from __future__ import annotations

import numpy as np
from openfermion import count_qubits

from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_spatial_chemist_integrals


def test_scbk_reduces_qubits_vs_jw_on_two_orbital_model() -> None:
    h1 = np.diag([0.05, 0.15]).astype(float)
    h2 = np.zeros((2, 2, 2, 2))
    qh_jw = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="jordan_wigner"
    )
    qh_scbk = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="symmetry_conserving_bravyi_kitaev"
    )
    assert count_qubits(qh_jw.operator) == 4
    assert count_qubits(qh_scbk.operator) == 2
    assert qh_scbk.n_qubits == 2


def test_scbk_single_orbital_active_space() -> None:
    h1 = np.array([[0.2]], dtype=float)
    h2 = np.zeros((1, 1, 1, 1))
    qh = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="symmetry_conserving_bravyi_kitaev"
    )
    assert qh.n_qubits == 0 or qh.n_qubits <= 2


def test_bk_preserves_qubit_count_on_two_orbital_model() -> None:
    h1 = np.diag([0.05, 0.15]).astype(float)
    h2 = np.zeros((2, 2, 2, 2))
    qh_bk = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="bravyi_kitaev"
    )
    assert count_qubits(qh_bk.operator) == 4

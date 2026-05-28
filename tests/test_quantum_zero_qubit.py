"""Zero-qubit Hamiltonian boundary tests."""

from __future__ import annotations

from openfermion.ops import QubitOperator

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.excited import QSE


def test_zero_qubit_constant_hamiltonian_dense_energy() -> None:
    op = QubitOperator((), 0.42)
    qh = QubitHamiltonian(operator=op, n_qubits=0, fermion_space=FermionSpace(0, 0))
    qse = QSE(qh, subspace_dim=1)
    r = qse.run_dense_reference()
    assert r.excitation_energies == []
    assert r.meta["method"] == "full_dense_subspace"


def test_zero_qubit_qse_dense_reference() -> None:
    op = QubitOperator((), -1.5)
    qh = QubitHamiltonian(operator=op, n_qubits=0, fermion_space=FermionSpace(0, 0))
    qse = QSE(qh, subspace_dim=1)
    r = qse.run_dense_reference()
    assert r.excitation_energies == []


def test_subspace_dim_clamped_to_hilbert_size() -> None:
    op = QubitOperator(((0, "Z"),), 0.2)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    qse = QSE(qh, subspace_dim=100)
    assert qse.subspace_dim == 2

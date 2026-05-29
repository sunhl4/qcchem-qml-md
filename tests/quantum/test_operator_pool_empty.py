"""Empty operator pool edge cases."""

from __future__ import annotations

import pytest
from openfermion.ops import QubitOperator

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool


def test_toy_pool_nonempty_for_two_qubits() -> None:
    op = QubitOperator(((0, "Z"),), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=2, fermion_space=None)
    pool = build_registered_operator_pool("toy_pair_xx", qh)
    assert len(pool) == 1


def test_uccsd_pool_falls_back_when_no_fermion_space() -> None:
    op = QubitOperator(((0, "Z"),), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=2, fermion_space=None)
    pool = build_registered_operator_pool("fermionic_uccsd", qh)
    assert len(pool) >= 1


def test_unknown_pool_id_raises() -> None:
    op = QubitOperator(((0, "Z"),), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    with pytest.raises(ValueError, match="Unknown operator pool id"):
        build_registered_operator_pool("___no_such_pool___", qh)

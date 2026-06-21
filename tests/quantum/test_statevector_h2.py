"""Tests without PySCF: tiny synthetic Hamiltonian."""

from __future__ import annotations

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.statevector import expectation_qubit_operator, hea_state


def test_hea_h2_two_qubit() -> None:
    h = QubitOperator("Z0", 0.5) + QubitOperator("Z1", 0.5) + QubitOperator("X0 X1", 0.1)
    qh = QubitHamiltonian(operator=h, n_qubits=2, fermion_space=FermionSpace(4, 2))
    v = VQE(qh, depth=2).run(maxiter=300, seed=1)
    st = hea_state(v.angles, 2, 2)
    e = float(np.real(expectation_qubit_operator(st, h, 2)))
    assert e < 0.5

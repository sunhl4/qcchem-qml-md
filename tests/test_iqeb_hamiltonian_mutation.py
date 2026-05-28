"""IQEB Hamiltonian mutation across outer rounds."""

from __future__ import annotations

from openfermion.ops import QubitOperator

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.iqeb import IQEBVQE


def test_iqeb_mutates_hamiltonian_and_selects_terms() -> None:
    op = QubitOperator(((0, "Z"),), 0.3) + QubitOperator((), 0.05)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    iqeb = IQEBVQE(qh, max_rounds=2, n_grads=1, pool_id="toy_pair_xx")
    result = iqeb.run(depth=1, seed=0)
    assert result.energy == result.vqe.energy
    assert isinstance(result.selected_pauli_strings, list)
    rounds = result.meta.get("iqeb_rounds") or []
    assert len(rounds) >= 1
    assert result.meta.get("pool_id") == "toy_pair_xx"

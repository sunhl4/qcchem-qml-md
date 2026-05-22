from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.excited import QSE
from qchem_stack.quantum.variational_branch import build_uccsd_variational_model

pytestmark = pytest.mark.l1_excited


def _h2_like_qh() -> QubitHamiltonian:
    op = QubitOperator(((0, "Z"),), -0.5) + QubitOperator(((1, "Z"),), -0.5)
    return QubitHamiltonian(
        operator=op,
        n_qubits=4,
        fermion_space=FermionSpace(n_spin_orbitals=4, n_electrons=2),
        meta={"fermion_to_qubit_map": "jordan_wigner"},
    )


def test_qse_uccsd_pauli_transitions_schedule_meta() -> None:
    qh = _h2_like_qh()
    exe = StatevectorHeaExecutor()
    model = build_uccsd_variational_model(qh, exe, trotter_steps=None)
    angles = np.zeros(model.n_params, dtype=float)
    qse = QSE(qh, subspace_dim=4)
    r = qse.run_from_uccsd_basis_pauli_transitions(
        angles,
        model.prepare_state,
        max_basis=3,
        shots_per_ij_term=64,
        seed=1,
    )
    sched = r.meta.get("qse_pauli_transition_schedule") or {}
    assert sched.get("n_transition_tasks", 0) > 0
    assert r.meta.get("basis_reference") == "uccsd_fermionic_singles"
    assert len(r.excitation_energies) >= 1

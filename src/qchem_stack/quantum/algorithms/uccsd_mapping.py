"""JW / BK reference states and fermion→qubit generator maps for UCCSD ansätze."""

from __future__ import annotations

import numpy as np
import openfermion as of
from openfermion import bravyi_kitaev, get_sparse_operator, jordan_wigner
from openfermion.ops import FermionOperator, QubitOperator

from qchem_stack.quantum.algorithms.tolerances import NUMERICAL_TOLERANCE


def occupied_string_creation_op(n_electrons: int) -> FermionOperator:
    op = FermionOperator(())
    for spin_orb_idx in range(int(n_electrons)):
        op *= FermionOperator(((int(spin_orb_idx), 1),), 1.0)
    return op


def map_fermion_generator(
    ferm_op: FermionOperator,
    mapping: str,
    *,
    n_spin_orbitals: int | None = None,
) -> QubitOperator:
    if mapping == "jordan_wigner":
        q = jordan_wigner(ferm_op)
    elif mapping == "bravyi_kitaev":
        q = bravyi_kitaev(ferm_op)
    elif mapping == "jkmn":
        from qchem_stack.chem.mappings.jkmn import jkmn

        if n_spin_orbitals is None:
            n_spin_orbitals = (
                max((idx for term in ferm_op.terms for idx, _ in term), default=-1) + 1
            )
        if int(n_spin_orbitals) <= 0:
            raise ValueError("JKMN generator map requires n_spin_orbitals > 0.")
        q = jkmn(ferm_op, n_qubits=int(n_spin_orbitals))
    else:
        raise ValueError(f"Unsupported fermion_to_qubit_map for UCCSDVQE: {mapping!r}")
    if not isinstance(q, QubitOperator):
        raise TypeError(f"Expected QubitOperator from OpenFermion map, got {type(q)}")
    return q


def reference_state_dense(*, mapping: str, n_spin_orbitals: int, n_electrons: int) -> np.ndarray:
    if mapping == "jordan_wigner":
        v = np.asarray(
            of.jw_hartree_fock_state(int(n_electrons), int(n_spin_orbitals)), dtype=np.complex128
        ).ravel()
    elif mapping == "bravyi_kitaev":
        fop = occupied_string_creation_op(int(n_electrons))
        q_op = bravyi_kitaev(fop)
        mat = get_sparse_operator(q_op, n_qubits=int(n_spin_orbitals))
        vac = np.zeros(2 ** int(n_spin_orbitals), dtype=np.complex128)
        vac[0] = 1.0
        v = np.asarray(mat @ vac, dtype=np.complex128).ravel()
    elif mapping == "jkmn":
        from qchem_stack.chem.mappings.jkmn import jkmn_reference_statevector

        v = jkmn_reference_statevector(
            n_spin_orbitals=int(n_spin_orbitals), n_electrons=int(n_electrons)
        )
    elif mapping == "hard_core_boson":
        from qchem_stack.chem.mappings.hcb import hcb_reference_statevector

        v = hcb_reference_statevector(
            n_spin_orbitals=int(n_spin_orbitals), n_electrons=int(n_electrons)
        )
    else:
        raise ValueError(f"Unsupported fermion_to_qubit_map for reference state: {mapping!r}")
    nrm = float(np.linalg.norm(v))
    if nrm < NUMERICAL_TOLERANCE:
        raise ValueError("UCCSD reference state has zero norm.")
    return v / nrm


def antihermitian_cluster_matrices(
    fermion_generators: list[FermionOperator],
    *,
    mapping: str,
    n_qubits: int,
    n_spin_orbitals: int | None = None,
) -> list[np.ndarray]:
    """Map fermionic cluster generators to anti-Hermitian dense matrices."""
    n_so = int(n_spin_orbitals if n_spin_orbitals is not None else n_qubits)
    mats: list[np.ndarray] = []
    for fer in fermion_generators:
        qop = map_fermion_generator(fer, mapping, n_spin_orbitals=n_so)
        sm = get_sparse_operator(qop, n_qubits=n_qubits)
        d = sm.toarray()
        a = d - np.conjugate(d.T)
        mats.append(np.asarray(a, dtype=np.complex128))
    return mats

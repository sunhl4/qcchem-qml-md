"""JW / BK reference states and fermion→qubit generator maps for UCCSD ansätze."""

from __future__ import annotations

import numpy as np
import openfermion as of
from openfermion import bravyi_kitaev, get_sparse_operator, jordan_wigner
from openfermion.ops import FermionOperator, QubitOperator


def occupied_string_creation_op(n_electrons: int) -> FermionOperator:
    op = FermionOperator(())
    for spin_orb_idx in range(int(n_electrons)):
        op *= FermionOperator(((int(spin_orb_idx), 1),), 1.0)
    return op


def map_fermion_generator(ferm_op: FermionOperator, mapping: str) -> QubitOperator:
    if mapping == "jordan_wigner":
        q = jordan_wigner(ferm_op)
    elif mapping == "bravyi_kitaev":
        q = bravyi_kitaev(ferm_op)
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
    else:
        raise ValueError(mapping)
    nrm = float(np.linalg.norm(v))
    if nrm < 1e-14:
        raise ValueError("UCCSD reference state has zero norm.")
    return v / nrm


def antihermitian_cluster_matrices(
    fermion_generators: list[FermionOperator],
    *,
    mapping: str,
    n_qubits: int,
) -> list[np.ndarray]:
    """Map fermionic cluster generators to anti-Hermitian dense matrices."""
    mats: list[np.ndarray] = []
    for fer in fermion_generators:
        qop = map_fermion_generator(fer, mapping)
        sm = get_sparse_operator(qop, n_qubits=n_qubits)
        d = sm.toarray()
        a = d - np.conjugate(d.T)
        mats.append(np.asarray(a, dtype=np.complex128))
    return mats

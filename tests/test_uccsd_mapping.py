"""UCCSD JW/BK mapping helpers."""

from __future__ import annotations

import numpy as np
from openfermion.ops import FermionOperator

from qchem_stack.quantum.algorithms.uccsd_mapping import (
    antihermitian_cluster_matrices,
    map_fermion_generator,
    reference_state_dense,
)


def test_map_fermion_generator_jw_is_qubit_operator() -> None:
    fer = FermionOperator(((0, 1), (1, 0)), 1.0)
    qop = map_fermion_generator(fer, "jordan_wigner")
    assert len(qop.terms) >= 1


def test_reference_state_dense_normalized() -> None:
    psi = reference_state_dense(mapping="jordan_wigner", n_spin_orbitals=4, n_electrons=2)
    assert psi.shape == (16,)
    assert abs(float(np.linalg.norm(psi)) - 1.0) < 1e-10


def test_antihermitian_cluster_matrices_shape() -> None:
    fer = FermionOperator(((0, 1), (1, 0)), 1.0)
    mats = antihermitian_cluster_matrices([fer], mapping="jordan_wigner", n_qubits=4)
    assert len(mats) == 1
    assert mats[0].shape == (16, 16)

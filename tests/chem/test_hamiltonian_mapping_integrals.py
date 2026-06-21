"""Integral transform edge cases for fermion-to-qubit mapping."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion import InteractionOperator

from qchem_stack.chem.hamiltonian_mapping import (
    _fermion_operator_to_qubits,
    _interaction_operator_to_qubits,
    _use_restricted_spatial_fermion_build,
)


def test_interaction_operator_jw_matches_fermion_path() -> None:
    h1 = np.diag([0.1, 0.2]).astype(float)
    h2 = np.zeros((2, 2, 2, 2))
    mol_op = InteractionOperator(0.05, h1, h2)
    q_jw = _interaction_operator_to_qubits(mol_op, "jordan_wigner")
    assert len(q_jw.terms) >= 1


def test_scbk_requires_active_fermion_count() -> None:
    h1 = np.diag([0.1, 0.2]).astype(float)
    h2 = np.zeros((2, 2, 2, 2))
    mol_op = InteractionOperator(0.0, h1, h2)
    with pytest.raises(ValueError, match="n_active_fermions"):
        _interaction_operator_to_qubits(
            mol_op,
            "symmetry_conserving_bravyi_kitaev",
            n_spin_orbitals=4,
        )


def test_unknown_mapping_raises() -> None:
    from openfermion import FermionOperator

    with pytest.raises(ValueError, match="Unknown fermion_qubit_mapping"):
        _fermion_operator_to_qubits(
            FermionOperator(), "not_a_mapping", n_spin_orbitals=2, n_active_fermions=2
        )


def test_jw_coeff_atol_only_for_jw() -> None:
    with pytest.raises(ValueError, match="jordan_wigner_coeff_atol"):
        _use_restricted_spatial_fermion_build(
            fermion_qubit_mapping="bravyi_kitaev",
            prefer_restricted_spatial_fermion_for_jordan_wigner=False,
            jordan_wigner_coeff_atol=1e-12,
        )

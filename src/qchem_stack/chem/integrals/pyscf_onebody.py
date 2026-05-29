from __future__ import annotations

from typing import Any, Literal

import numpy as np


def _spatial_one_body_to_fermion_operator(h1_spatial: np.ndarray) -> Any:
    from openfermion import FermionOperator

    h1 = np.asarray(h1_spatial, dtype=float)
    n = int(h1.shape[0])
    out = FermionOperator()
    for p in range(n):
        for q in range(n):
            c = float(h1[p, q])
            if abs(c) < 1e-14:
                continue
            out += FermionOperator(((2 * p, 1), (2 * q, 0)), c)
            out += FermionOperator(((2 * p + 1, 1), (2 * q + 1, 0)), c)
    return out


def _transform_ao_to_mo(ao_mat: np.ndarray, mo_coeff: np.ndarray) -> np.ndarray:
    c = np.asarray(mo_coeff, dtype=float)
    a = np.asarray(ao_mat, dtype=float)
    return np.asarray(c.T @ a @ c, dtype=float)


def one_electron_operator_fermion_from_rhf(
    rhf: Any,
    oper: Literal["kin", "nuc", "hcore", "ovlp", "r", "rr", "dm"],
    *,
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> Any:
    mf = rhf.mf
    mol = mf.mol
    mo = np.asarray(mf.mo_coeff, dtype=float)
    if oper == "kin":
        h = mol.intor_symmetric("int1e_kin")
        return _spatial_one_body_to_fermion_operator(_transform_ao_to_mo(h, mo))
    if oper == "nuc":
        h = mol.intor_symmetric("int1e_nuc")
        return _spatial_one_body_to_fermion_operator(_transform_ao_to_mo(h, mo))
    if oper == "hcore":
        h = mf.get_hcore()
        return _spatial_one_body_to_fermion_operator(_transform_ao_to_mo(h, mo))
    if oper == "ovlp":
        h = mf.get_ovlp()
        return _spatial_one_body_to_fermion_operator(_transform_ao_to_mo(h, mo))
    with mol.with_common_origin(tuple(map(float, origin))):
        if oper in ("r", "dm"):
            mats = np.asarray(mol.intor("int1e_r"), dtype=float).reshape(
                3, mo.shape[0], mo.shape[0]
            )
            if oper == "dm":
                mats = -mats
            return [_spatial_one_body_to_fermion_operator(_transform_ao_to_mo(m, mo)) for m in mats]
        if oper == "rr":
            mats = np.asarray(mol.intor("int1e_rr"), dtype=float).reshape(
                9, mo.shape[0], mo.shape[0]
            )
            return [_spatial_one_body_to_fermion_operator(_transform_ao_to_mo(m, mo)) for m in mats]
    raise ValueError(f"Unsupported one-electron operator key: {oper!r}")


def one_electron_operator_pauli_from_rhf(
    rhf: Any,
    oper: Literal["kin", "nuc", "hcore", "ovlp", "r", "rr", "dm"],
    *,
    origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    fermion_qubit_mapping: Literal[
        "jordan_wigner",
        "bravyi_kitaev",
        "symmetry_conserving_bravyi_kitaev",
    ] = "jordan_wigner",
    n_electrons: int | None = None,
) -> Any:
    from openfermion import bravyi_kitaev, jordan_wigner, symmetry_conserving_bravyi_kitaev

    fop = one_electron_operator_fermion_from_rhf(rhf, oper, origin=origin)

    def _map_one(op: Any) -> Any:
        if fermion_qubit_mapping == "jordan_wigner":
            return jordan_wigner(op)
        if fermion_qubit_mapping == "bravyi_kitaev":
            return bravyi_kitaev(op)
        n_spin_orbitals = int(2 * np.asarray(rhf.mf.mo_coeff).shape[1])
        if n_electrons is None:
            raise ValueError(
                "compute_one_electron_operator_pauli(..., fermion_qubit_mapping='symmetry_conserving_bravyi_kitaev') "
                "requires n_electrons."
            )
        return symmetry_conserving_bravyi_kitaev(op, n_spin_orbitals, int(n_electrons))

    if isinstance(fop, list):
        return [_map_one(x) for x in fop]
    return _map_one(fop)

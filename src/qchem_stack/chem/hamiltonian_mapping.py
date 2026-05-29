"""Fermion-to-qubit mapping helpers (chem layer)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from openfermion import (
    InteractionOperator,
    bravyi_kitaev,
    get_fermion_operator,
    jordan_wigner,
    symmetry_conserving_bravyi_kitaev,
)

from qchem_stack.chem.jordan_wigner_sparse import jordan_wigner_interaction_operator_sparse
from qchem_stack.chem.mappings.jkmn import jkmn

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from .hamiltonian_meta import FermionQubitMappingName


def _fermion_operator_to_qubits(
    fermion_op: Any,
    mapping: FermionQubitMappingName,
    *,
    n_spin_orbitals: int,
    n_active_fermions: int,
) -> QubitOperator:
    """Map a fermionic operator to qubits (JW / BK / SCBK) without a dense spin-orbital ERI tensor."""
    if mapping == "jordan_wigner":
        return cast("QubitOperator", jordan_wigner(fermion_op))
    if mapping == "bravyi_kitaev":
        return cast("QubitOperator", bravyi_kitaev(fermion_op))
    if mapping == "symmetry_conserving_bravyi_kitaev":
        return cast(
            "QubitOperator",
            symmetry_conserving_bravyi_kitaev(
                fermion_op, int(n_spin_orbitals), int(n_active_fermions)
            ),
        )
    if mapping == "jkmn":
        return jkmn(fermion_op, n_qubits=int(n_spin_orbitals))
    if mapping == "hard_core_boson":
        raise ValueError(
            "hard_core_boson mapping requires spatial MO integrals "
            "(use qubit_hamiltonian_from_spatial_chemist_integrals)."
        )
    raise ValueError(f"Unknown fermion_qubit_mapping: {mapping!r}")


def _interaction_operator_to_qubits(
    mol_op: InteractionOperator,
    mapping: FermionQubitMappingName,
    *,
    n_spin_orbitals: int | None = None,
    n_active_fermions: int | None = None,
    jordan_wigner_coeff_atol: float | None = None,
) -> QubitOperator:
    if mapping == "jordan_wigner":
        return jordan_wigner_interaction_operator_sparse(mol_op, atol=jordan_wigner_coeff_atol)
    n_spin = int(
        n_spin_orbitals if n_spin_orbitals is not None else mol_op.one_body_tensor.shape[0]
    )
    if mapping == "bravyi_kitaev":
        return cast("QubitOperator", bravyi_kitaev(mol_op))
    if mapping == "symmetry_conserving_bravyi_kitaev":
        if n_active_fermions is None:
            raise ValueError(
                "symmetry_conserving_bravyi_kitaev requires n_spin_orbitals and n_active_fermions "
                "(OpenFermion SCBK removes two qubits vs JW on the same active space)."
            )
        fo = get_fermion_operator(mol_op)
        return cast(
            "QubitOperator",
            symmetry_conserving_bravyi_kitaev(fo, n_spin, int(n_active_fermions)),
        )
    if mapping == "jkmn":
        fo = get_fermion_operator(mol_op)
        return jkmn(fo, n_qubits=n_spin)
    if mapping == "hard_core_boson":
        raise ValueError(
            "hard_core_boson mapping requires spatial MO integrals "
            "(use qubit_hamiltonian_from_spatial_chemist_integrals)."
        )
    raise ValueError(f"Unknown fermion_qubit_mapping: {mapping!r}")


def _qubit_build_meta(
    *,
    fermion_qubit_mapping: FermionQubitMappingName,
    build_route: str,
    jordan_wigner_coeff_atol: float | None = None,
) -> dict[str, Any]:
    """Hamiltonian meta for mapping + integral build route (``jw_build`` kept for repro)."""
    out: dict[str, Any] = {
        "fermion_to_qubit_map": fermion_qubit_mapping,
        "qubit_build": build_route,
        "jw_build": build_route,
    }
    if jordan_wigner_coeff_atol is not None:
        out["jordan_wigner_coeff_atol"] = float(jordan_wigner_coeff_atol)
    return out


def _use_restricted_spatial_fermion_build(
    *,
    fermion_qubit_mapping: FermionQubitMappingName,
    prefer_restricted_spatial_fermion_for_jordan_wigner: bool,
    jordan_wigner_coeff_atol: float | None,
) -> bool:
    """Spatial-MO fermion build avoids dense (2*norb)^4 spin ERI for BK/SCBK and optional JW."""
    if fermion_qubit_mapping in (
        "bravyi_kitaev",
        "symmetry_conserving_bravyi_kitaev",
        "jkmn",
        "hard_core_boson",
    ):
        if jordan_wigner_coeff_atol is not None:
            raise ValueError(
                "jordan_wigner_coeff_atol applies only to fermion_qubit_mapping='jordan_wigner' "
                "on the InteractionOperator path."
            )
        return True
    if fermion_qubit_mapping == "jordan_wigner":
        if jordan_wigner_coeff_atol is not None:
            return False
        return bool(prefer_restricted_spatial_fermion_for_jordan_wigner)
    return False

"""Build restricted active-space quantum problems from config / references."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.molecular_problem import (
    RestrictedActiveSpaceQuantumProblem,
    build_restricted_active_space_quantum_problem,
)

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian_meta import FermionQubitMappingName
    from qchem_stack.config import ExperimentConfig


def restricted_active_space_quantum_problem_from_config(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference | None = None,
    *,
    n_active_orbitals: int | None = None,
    n_active_electrons: int | None = None,
    fermion_qubit_mapping: FermionQubitMappingName | None = None,
    prefer_restricted_spatial_fermion_for_jordan_wigner: bool | None = None,
    jordan_wigner_coeff_atol: float | None = None,
) -> RestrictedActiveSpaceQuantumProblem:
    """Registry-backed entry for :class:`RestrictedActiveSpaceQuantumProblem`.

    Resolves active-space sizes and JW flags from ``cfg.active_space`` when omitted.
    """
    from qchem_stack.chem.bridges.reference_factory import (
        classical_mean_field_reference_from_config,
    )
    from qchem_stack.config.active_space_helpers import (
        resolve_fermion_qubit_mapping,
        resolve_n_electrons,
        resolve_n_orbitals,
    )

    ref = reference or classical_mean_field_reference_from_config(cfg)
    active = cfg.active_space
    na = int(n_active_orbitals if n_active_orbitals is not None else resolve_n_orbitals(active))
    ne = int(n_active_electrons if n_active_electrons is not None else resolve_n_electrons(active))
    mapping = fermion_qubit_mapping or resolve_fermion_qubit_mapping(active)
    prefer = prefer_restricted_spatial_fermion_for_jordan_wigner
    if prefer is None:
        prefer = bool(active.jw.prefer_restricted_spatial)
    atol = jordan_wigner_coeff_atol
    if atol is None:
        atol = active.jw.coeff_atol
    return build_restricted_active_space_quantum_problem(
        ref,
        n_active_orbitals=na,
        n_active_electrons=ne,
        fermion_qubit_mapping=mapping,
        prefer_restricted_spatial_fermion_for_jordan_wigner=prefer,
        jordan_wigner_coeff_atol=atol,
    )


__all__ = ["restricted_active_space_quantum_problem_from_config"]

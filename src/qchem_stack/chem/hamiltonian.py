"""Qubit Hamiltonian build facade (chem layer; do not import orchestration).

Implementation is split across ``hamiltonian_meta``, ``hamiltonian_mapping``, and
``hamiltonian_build``; this module re-exports the public API for backward compatibility.
"""

from __future__ import annotations

from .hamiltonian_build import (
    QubitHamiltonian,
    fermionic_active_space_interaction_operator_from_canonical_pack,
    fermionic_active_space_interaction_operator_from_classical_reference,
    molecular_hamiltonian_from_canonical_active_space_pack,
    molecular_hamiltonian_from_classical_reference,
    qubit_hamiltonian_from_active_space_fermionic_operator,
    qubit_hamiltonian_from_compact_restricted_active_space,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from .hamiltonian_meta import (
    FermionQubitMappingName,
    hamiltonian_fingerprint_from_qubit_operator,
)


def molecular_hamiltonian_from_pyscf(
    rhf,
    *,
    n_active_orbitals: int,
    n_active_electrons: int,
    fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner",
    prefer_restricted_spatial_fermion_for_jordan_wigner: bool = False,
    jordan_wigner_coeff_atol: float | None = None,
) -> QubitHamiltonian:
    """Compatibility alias for PySCF ``PySCFRHFResult`` inputs.

    Prefer :func:`build_pre_quantum_input` or
    :func:`molecular_hamiltonian_from_classical_reference` on a
    :class:`~qchem_stack.chem.bridges.mean_field_reference.ClassicalMeanFieldReference`.
    """
    import warnings

    from qchem_stack.chem.bridges.driver_meta import fork_driver_meta
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference

    warnings.warn(
        "molecular_hamiltonian_from_pyscf is deprecated; use build_pre_quantum_input or "
        "molecular_hamiltonian_from_classical_reference.",
        DeprecationWarning,
        stacklevel=2,
    )
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=fork_driver_meta(rhf.driver_meta),
    )
    return molecular_hamiltonian_from_classical_reference(
        ref,
        n_active_orbitals=n_active_orbitals,
        n_active_electrons=n_active_electrons,
        fermion_qubit_mapping=fermion_qubit_mapping,
        prefer_restricted_spatial_fermion_for_jordan_wigner=prefer_restricted_spatial_fermion_for_jordan_wigner,
        jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
    )


__all__ = [
    "FermionQubitMappingName",
    "QubitHamiltonian",
    "fermionic_active_space_interaction_operator_from_canonical_pack",
    "fermionic_active_space_interaction_operator_from_classical_reference",
    "hamiltonian_fingerprint_from_qubit_operator",
    "molecular_hamiltonian_from_canonical_active_space_pack",
    "molecular_hamiltonian_from_classical_reference",
    "molecular_hamiltonian_from_pyscf",
    "qubit_hamiltonian_from_active_space_fermionic_operator",
    "qubit_hamiltonian_from_compact_restricted_active_space",
    "qubit_hamiltonian_from_spatial_chemist_integrals",
]

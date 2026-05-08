"""Restricted closed-shell active-space objects for variational quantum workflows.

Analogous to InQuanto-PySCF ``get_system()``-style tuples:
:class:`~qchem_stack.chem.restricted_integral_operator.RestrictedActiveSpaceIntegralOperatorCompact`
(PySCF-compact MO ERIs + pandas ``df`` hooks),
:class:`openfermion.InteractionOperator`, :class:`~qchem_stack.chem.fermion.FermionSpace`,
Jordan–Wigner HF reference, and :class:`~qchem_stack.chem.hamiltonian.QubitHamiltonian`.

AO mean-field handles mirror ``get_system_ao`` via :meth:`qchem_stack.chem.drivers.pyscf_driver.PySCFDriver.get_system_ao`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from openfermion import InteractionOperator, jw_hartree_fock_state

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import (
    FermionQubitMappingName,
    QubitHamiltonian,
    qubit_hamiltonian_from_active_space_fermionic_operator,
    qubit_hamiltonian_from_compact_restricted_active_space,
)
from qchem_stack.chem.restricted_integral_operator import (
    RestrictedActiveSpaceIntegralOperatorCompact,
)


def _pyscf_symmetry_snapshot(mf: Any) -> dict[str, Any]:
    mol = getattr(mf, "mol", None)
    if mol is None:
        return {"pyscf_symmetry_detected": False}
    symm_orb = getattr(mol, "symm_orb", None)
    detected = symm_orb is not None and len(symm_orb) > 0
    subgroup = getattr(mol, "groupname", None)
    return {
        "pyscf_symmetry_detected": bool(detected),
        "pyscf_symmetry_subgroup": subgroup,
    }


@dataclass(frozen=True)
class RestrictedActiveSpaceQuantumProblem:
    """MO active-space fermionic Hamiltonian + JW HF reference + mapped qubit Hamiltonian."""

    compact_mo_operator: RestrictedActiveSpaceIntegralOperatorCompact
    interaction_operator: InteractionOperator
    fermion_space: FermionSpace
    hartree_fock_state_jw: np.ndarray
    qubit_hamiltonian: QubitHamiltonian
    meta: dict[str, Any] = field(default_factory=dict)


def build_restricted_active_space_quantum_problem(
    rhf: ClassicalMeanFieldReference,
    *,
    n_active_orbitals: int,
    n_active_electrons: int,
    fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner",
    prefer_restricted_spatial_fermion_for_jordan_wigner: bool = False,
    jordan_wigner_coeff_atol: float | None = None,
) -> RestrictedActiveSpaceQuantumProblem:
    """Construct quantum-problem pieces after a unified classical mean-field reference.

    ``hartree_fock_state_jw`` is always the OpenFermion **Jordan–Wigner** computational vector on
    ``fermion_space.n_spin_orbitals`` qubits. For BK / SCBK mappings, derive reference states separately.

    ``prefer_restricted_spatial_fermion_for_jordan_wigner`` uses the spatial-MO fermion build for JW only;
    ``jordan_wigner_coeff_atol`` applies only to the default InteractionOperator mapping and must be
    ``None`` when that flag is enabled with Jordan–Wigner.
    """
    if rhf.backend_tag() == "pyscf":
        try:
            from pyscf import scf as scf_mod

            if isinstance(rhf.mf, (scf_mod.rohf.ROHF, scf_mod.uhf.UHF)):
                raise ValueError(
                    "Restricted active-space quantum problem currently supports RHF references only. "
                    "Use scf.method=RHF or extend with spin-resolved open-shell integrals."
                )
        except ImportError:
            pass
    pack = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        rhf,
        n_active_orbitals=n_active_orbitals,
        n_active_electrons=n_active_electrons,
    )
    compact = pack.compact
    mol_op = compact.to_interaction_operator()
    n_so = int(mol_op.one_body_tensor.shape[0])
    fs = FermionSpace(n_spin_orbitals=n_so, n_electrons=n_active_electrons)
    if prefer_restricted_spatial_fermion_for_jordan_wigner and fermion_qubit_mapping == "jordan_wigner":
        if jordan_wigner_coeff_atol is not None:
            raise ValueError(
                "jordan_wigner_coeff_atol applies only to the InteractionOperator JW path; "
                "use prefer_restricted_spatial_fermion_for_jordan_wigner=False, or pass atol=None."
            )
        qh = qubit_hamiltonian_from_compact_restricted_active_space(
            compact,
            fs,
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
            fermion_qubit_mapping=fermion_qubit_mapping,
            rhf=rhf,
        )
    else:
        qh = qubit_hamiltonian_from_active_space_fermionic_operator(
            mol_op,
            fs,
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
            fermion_qubit_mapping=fermion_qubit_mapping,
            rhf=rhf,
            jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
        )
    psi = np.asarray(
        jw_hartree_fock_state(int(fs.n_electrons), int(fs.n_spin_orbitals)),
        dtype=np.complex128,
    ).ravel()
    nrm = float(np.linalg.norm(psi))
    if nrm < 1e-14:
        raise ValueError("JW Hartree–Fock state has zero norm.")
    psi = psi / nrm
    meta = {
        "schema": "restricted_active_space_quantum_problem_v1",
        "hartree_fock_reference_basis": "openfermion_jordan_wigner_spin_orbital_order",
        "fermion_qubit_mapping_used_for_qubit_hamiltonian": fermion_qubit_mapping,
        "compact_integral_storage_schema": compact.storage_schema,
    }
    if rhf.backend_tag() == "pyscf":
        meta.update(_pyscf_symmetry_snapshot(rhf.mf))
    else:
        meta["upstream_classical_software_tag"] = rhf.backend_tag()
    meta["compact_layout"] = dict(compact.symmetry_meta)
    meta["jw_build"] = qh.meta.get("jw_build", "interaction_operator")
    return RestrictedActiveSpaceQuantumProblem(
        compact_mo_operator=compact,
        interaction_operator=mol_op,
        fermion_space=fs,
        hartree_fock_state_jw=psi,
        qubit_hamiltonian=qh,
        meta=meta,
    )

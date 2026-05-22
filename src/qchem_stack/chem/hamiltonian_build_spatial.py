"""Qubit Hamiltonian assembly from raw spatial MO integrals."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from openfermion import InteractionOperator
from openfermion.chem.molecular_data import spinorb_from_spatial

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.spatial_restricted_fermion import (
    restricted_spatial_integrals_to_fermion_operator,
)

from .hamiltonian_build_assembly import assemble_qubit_hamiltonian
from .hamiltonian_mapping import (
    _fermion_operator_to_qubits,
    _interaction_operator_to_qubits,
    _use_restricted_spatial_fermion_build,
)

if TYPE_CHECKING:
    from .hamiltonian_build import QubitHamiltonian
    from .hamiltonian_meta import FermionQubitMappingName


def qubit_hamiltonian_from_spatial_chemist_integrals(
    constant: float,
    h1: np.ndarray,
    h2: np.ndarray,
    n_electrons: int,
    *,
    fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner",
    integral_source: str = "spatial_chemist_integrals",
    meta_extra: dict[str, Any] | None = None,
    pyscf_driver_meta: dict[str, Any] | None = None,
    classical_driver_meta: dict[str, Any] | None = None,
    prefer_restricted_spatial_fermion_for_jordan_wigner: bool = False,
    jordan_wigner_coeff_atol: float | None = None,
) -> QubitHamiltonian:
    """Map spatial MO integrals to qubits via OpenFermion (Tangelo-style convention).

    ``h2`` must be **raw** PySCF MO chemist ERIs (same layout as ``ao2mo.restore(1, ...)`` /
    CASCI ``get_h2eff``). They are reordered with
    :func:`~qchem_stack.chem.integral_convention.spatial_mo_eri_pyscf_to_openfermion_mo_ordering`.
    """
    from qchem_stack.chem.integral_convention import (
        restore_packed_mo_eri_chemist,
        spatial_mo_eri_pyscf_to_openfermion_mo_ordering,
    )

    h1a = np.asarray(h1, dtype=float)
    h2_raw = np.asarray(h2, dtype=float)
    norb = int(h1a.shape[0])
    if h1a.shape != (norb, norb):
        raise ValueError("h1 must be (norb, norb)")
    if h2_raw.ndim == 2:
        h2_dense = restore_packed_mo_eri_chemist(h2_raw, norb)
    elif h2_raw.shape == (norb, norb, norb, norb):
        h2_dense = h2_raw
    else:
        raise ValueError("h2 must be (norb, norb, norb, norb) or packed (npair, npair)")
    h2a = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(h2_dense)
    if n_electrons < 0 or n_electrons > 2 * norb or n_electrons % 2 != 0:
        raise ValueError("n_electrons must be even and fit in 2*norb spin orbitals")

    n_spin = 2 * norb

    if _use_restricted_spatial_fermion_build(
        fermion_qubit_mapping=fermion_qubit_mapping,
        prefer_restricted_spatial_fermion_for_jordan_wigner=prefer_restricted_spatial_fermion_for_jordan_wigner,
        jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
    ):
        fo = restricted_spatial_integrals_to_fermion_operator(float(constant), h1a, h2a)
        qop = _fermion_operator_to_qubits(
            fo,
            fermion_qubit_mapping,
            n_spin_orbitals=n_spin,
            n_active_fermions=n_electrons,
        )
        qubit_build = "restricted_spatial_fermion_operator"
    else:
        h1_so, h2_so = spinorb_from_spatial(h1a, h2a)
        mol_op = InteractionOperator(float(constant), h1_so, 0.5 * h2_so)
        qop = _interaction_operator_to_qubits(
            mol_op,
            fermion_qubit_mapping,
            n_spin_orbitals=n_spin,
            n_active_fermions=n_electrons,
            jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
        )
        qubit_build = "interaction_operator"
    fs = FermionSpace(n_spin_orbitals=n_spin, n_electrons=n_electrons)
    return assemble_qubit_hamiltonian(
        qop,
        fs,
        fermion_qubit_mapping=fermion_qubit_mapping,
        build_route=qubit_build,
        n_active_orbitals=norb,
        n_active_electrons=n_electrons,
        integral_source=integral_source,
        integral_openfermion_bridge="pyscf_tangelo_openfermion_v1",
        jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
        meta_extra=meta_extra,
        pyscf_driver_meta=pyscf_driver_meta,
        classical_driver_meta=classical_driver_meta,
    )

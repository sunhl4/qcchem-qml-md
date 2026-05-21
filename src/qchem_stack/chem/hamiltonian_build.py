"""Qubit Hamiltonian assembly from classical / active-space integrals (chem layer)."""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from openfermion import InteractionOperator
from openfermion.chem.molecular_data import spinorb_from_spatial
from openfermion.linalg import get_sparse_operator

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
    from openfermion.ops import QubitOperator

    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.restricted_integral_operator import (
        RestrictedActiveSpaceIntegralOperatorCompact,
    )

    from .hamiltonian_meta import FermionQubitMappingName


@dataclass
class QubitHamiltonian:
    """Qubit operator from a molecular InteractionOperator + sparse cache."""

    operator: QubitOperator
    n_qubits: int
    fermion_space: FermionSpace | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def sparse_matrix(self) -> Any:
        return get_sparse_operator(self.operator, n_qubits=self.n_qubits)


def molecular_hamiltonian_from_canonical_active_space_pack(
    pack: CanonicalActiveSpaceIntegralPack,
    *,
    n_active_orbitals: int,
    n_active_electrons: int,
    fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner",
    prefer_restricted_spatial_fermion_for_jordan_wigner: bool = False,
    jordan_wigner_coeff_atol: float | None = None,
    classical_reference_for_meta: ClassicalMeanFieldReference | None = None,
) -> QubitHamiltonian:
    """Build qubit Hamiltonian from :class:`~qchem_stack.chem.bridges.canonical_integral_pack.CanonicalActiveSpaceIntegralPack`."""
    from qchem_stack.chem.bridges.canonical_integral_pack import (
        CanonicalActiveSpaceIntegralPack as CanonicalPack,
    )

    if not isinstance(pack, CanonicalPack):
        raise TypeError(f"expected CanonicalActiveSpaceIntegralPack, got {type(pack)!r}")
    compact = pack.compact
    if int(compact.n_active_orbitals) != int(n_active_orbitals) or int(
        compact.n_active_electrons
    ) != int(n_active_electrons):
        raise ValueError(
            f"active-space mismatch: pack compact has n_act={compact.n_active_orbitals}, "
            f"ne={compact.n_active_electrons}; got n_active_orbitals={n_active_orbitals}, "
            f"n_active_electrons={n_active_electrons}."
        )
    mol_op = compact.to_interaction_operator()
    n_so = int(mol_op.one_body_tensor.shape[0])
    fs = FermionSpace(n_spin_orbitals=n_so, n_electrons=n_active_electrons)

    if _use_restricted_spatial_fermion_build(
        fermion_qubit_mapping=fermion_qubit_mapping,
        prefer_restricted_spatial_fermion_for_jordan_wigner=prefer_restricted_spatial_fermion_for_jordan_wigner,
        jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
    ):
        if (
            prefer_restricted_spatial_fermion_for_jordan_wigner
            and fermion_qubit_mapping != "jordan_wigner"
        ):
            raise ValueError(
                "prefer_restricted_spatial_fermion_for_jordan_wigner applies to "
                "fermion_qubit_mapping='jordan_wigner' only; BK/SCBK use the spatial "
                "fermion path automatically without this flag."
            )
        return qubit_hamiltonian_from_compact_restricted_active_space(
            compact,
            fs,
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
            fermion_qubit_mapping=fermion_qubit_mapping,
            rhf=classical_reference_for_meta,
            canonical_pack=pack,
        )

    return qubit_hamiltonian_from_active_space_fermionic_operator(
        mol_op,
        fs,
        n_active_orbitals=n_active_orbitals,
        n_active_electrons=n_active_electrons,
        fermion_qubit_mapping=fermion_qubit_mapping,
        rhf=classical_reference_for_meta,
        jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
        canonical_pack=pack,
    )


def molecular_hamiltonian_from_classical_reference(
    reference: ClassicalMeanFieldReference,
    n_active_orbitals: int,
    n_active_electrons: int,
    *,
    fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner",
    prefer_restricted_spatial_fermion_for_jordan_wigner: bool = False,
    jordan_wigner_coeff_atol: float | None = None,
) -> QubitHamiltonian:
    """Build active-space molecular Hamiltonian from backend-agnostic mean-field reference.

    .. deprecated::
        Prefer :func:`qchem_stack.chem.pre_quantum_build.build_pre_quantum_input` or
        :func:`qchem_stack.orchestration.pipeline.run_pipeline_from_config` for full
        ``PreQuantumInput`` / repro metadata.
    """

    warnings.warn(
        "molecular_hamiltonian_from_classical_reference is deprecated; use "
        "qchem_stack.chem.pre_quantum_build.build_pre_quantum_input or the YAML pipeline.",
        DeprecationWarning,
        stacklevel=2,
    )
    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack

    pack = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        reference,
        n_active_orbitals=n_active_orbitals,
        n_active_electrons=n_active_electrons,
    )
    return molecular_hamiltonian_from_canonical_active_space_pack(
        pack,
        n_active_orbitals=n_active_orbitals,
        n_active_electrons=n_active_electrons,
        fermion_qubit_mapping=fermion_qubit_mapping,
        prefer_restricted_spatial_fermion_for_jordan_wigner=prefer_restricted_spatial_fermion_for_jordan_wigner,
        jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
        classical_reference_for_meta=reference,
    )


def fermionic_active_space_interaction_operator_from_classical_reference(
    reference: ClassicalMeanFieldReference,
    *,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> tuple[InteractionOperator, FermionSpace]:
    """MO active-space :class:`InteractionOperator` + :class:`FermionSpace` from unified reference."""
    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack

    pack = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        reference,
        n_active_orbitals=n_active_orbitals,
        n_active_electrons=n_active_electrons,
    )
    return fermionic_active_space_interaction_operator_from_canonical_pack(pack)


def fermionic_active_space_interaction_operator_from_canonical_pack(
    pack: CanonicalActiveSpaceIntegralPack,
) -> tuple[InteractionOperator, FermionSpace]:
    from qchem_stack.chem.bridges.canonical_integral_pack import (
        CanonicalActiveSpaceIntegralPack as CanonicalPack,
    )

    if not isinstance(pack, CanonicalPack):
        raise TypeError(f"expected CanonicalActiveSpaceIntegralPack, got {type(pack)!r}")
    mol_op = pack.compact.to_interaction_operator()
    n_so = int(mol_op.one_body_tensor.shape[0])
    fs = FermionSpace(n_spin_orbitals=n_so, n_electrons=pack.compact.n_active_electrons)
    return mol_op, fs


def qubit_hamiltonian_from_active_space_fermionic_operator(
    mol_op: InteractionOperator,
    fermion_space: FermionSpace,
    *,
    n_active_orbitals: int,
    n_active_electrons: int,
    fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner",
    rhf: ClassicalMeanFieldReference | None = None,
    jordan_wigner_coeff_atol: float | None = None,
    canonical_pack: CanonicalActiveSpaceIntegralPack | None = None,
    integral_source: str | None = None,
    integral_openfermion_bridge: str | None = None,
) -> QubitHamiltonian:
    """Map a pre-built fermionic active-space operator to qubits (shared by pipeline helpers)."""
    n_spin = int(fermion_space.n_spin_orbitals)
    qop = _interaction_operator_to_qubits(
        mol_op,
        fermion_qubit_mapping,
        n_spin_orbitals=n_spin,
        n_active_fermions=n_active_electrons,
        jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
    )
    return assemble_qubit_hamiltonian(
        qop,
        fermion_space,
        fermion_qubit_mapping=fermion_qubit_mapping,
        build_route="interaction_operator",
        n_active_orbitals=n_active_orbitals,
        n_active_electrons=n_active_electrons,
        rhf=rhf,
        canonical_pack=canonical_pack,
        integral_source=integral_source,
        integral_openfermion_bridge=integral_openfermion_bridge,
        jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
    )


def qubit_hamiltonian_from_compact_restricted_active_space(
    compact: RestrictedActiveSpaceIntegralOperatorCompact,
    fermion_space: FermionSpace,
    *,
    n_active_orbitals: int,
    n_active_electrons: int,
    fermion_qubit_mapping: FermionQubitMappingName = "jordan_wigner",
    rhf: ClassicalMeanFieldReference | None = None,
    jordan_wigner_coeff_atol: float | None = None,
    canonical_pack: CanonicalActiveSpaceIntegralPack | None = None,
    integral_source: str | None = None,
    integral_openfermion_bridge: str | None = None,
) -> QubitHamiltonian:
    """Map compact MO integrals to qubits.

    For ``bravyi_kitaev`` and ``symmetry_conserving_bravyi_kitaev``, uses spatial MO integrals →
    :class:`openfermion.FermionOperator` (no dense spin-orbital ERI). For ``jordan_wigner``, the same
    spatial path is used when ``prefer_restricted_spatial_fermion_for_jordan_wigner`` is set; otherwise
    the InteractionOperator + optional sparse JW path is used (required when ``jordan_wigner_coeff_atol`` is set).
    """
    from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering

    if not _use_restricted_spatial_fermion_build(
        fermion_qubit_mapping=fermion_qubit_mapping,
        prefer_restricted_spatial_fermion_for_jordan_wigner=True,
        jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
    ):
        mol_op = compact.to_interaction_operator()
        return qubit_hamiltonian_from_active_space_fermionic_operator(
            mol_op,
            fermion_space,
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
            fermion_qubit_mapping=fermion_qubit_mapping,
            rhf=rhf,
            jordan_wigner_coeff_atol=jordan_wigner_coeff_atol,
            canonical_pack=canonical_pack,
            integral_source=integral_source,
            integral_openfermion_bridge=integral_openfermion_bridge,
        )

    h2_of = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(compact.dense_h2_chemist_spatial())
    h1 = np.asarray(compact.h1_active_mo, dtype=float)
    fo = restricted_spatial_integrals_to_fermion_operator(float(compact.constant), h1, h2_of)
    n_spin = int(fermion_space.n_spin_orbitals)
    qop = _fermion_operator_to_qubits(
        fo,
        fermion_qubit_mapping,
        n_spin_orbitals=n_spin,
        n_active_fermions=n_active_electrons,
    )
    return assemble_qubit_hamiltonian(
        qop,
        fermion_space,
        fermion_qubit_mapping=fermion_qubit_mapping,
        build_route="restricted_spatial_fermion_operator",
        n_active_orbitals=n_active_orbitals,
        n_active_electrons=n_active_electrons,
        rhf=rhf,
        canonical_pack=canonical_pack,
        integral_source=integral_source,
        integral_openfermion_bridge=integral_openfermion_bridge,
    )


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
    By default, integrals are promoted with :func:`openfermion.chem.molecular_data.spinorb_from_spatial`,
    then passed to :class:`openfermion.InteractionOperator` with a **0.5** factor on the spin-orbital two-body
    block (see SandboxAQ Tangelo ``SecondQuantizedMolecule._get_fermionic_hamiltonian``).

    Set ``prefer_restricted_spatial_fermion_for_jordan_wigner=True`` with ``fermion_qubit_mapping='jordan_wigner'``
    to build a :class:`openfermion.FermionOperator` directly from spatial MO blocks (no dense ``(2*norb)^4``
    spin-orbital ERI array). ``jordan_wigner_coeff_atol`` applies only to the InteractionOperator JW path and
    must stay ``None`` when using that spatial-fermion shortcut.

    Args:
        jordan_wigner_coeff_atol: Optional positive cutoff on the InteractionOperator JW path: shells whose
            combined coefficient magnitude is ``<= atol`` are skipped (fewer Pauli accumulations when tensors
            are sparse). ``None`` or non-positive values preserve OpenFermion's exact JW aggregation.
    """
    from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering

    h1a = np.asarray(h1, dtype=float)
    h2a = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(np.asarray(h2, dtype=float))
    norb = int(h1a.shape[0])
    if h1a.shape != (norb, norb):
        raise ValueError("h1 must be (norb, norb)")
    if h2a.ndim == 2:
        from pyscf import ao2mo

        packed = norb * (norb + 1) // 2
        if h2a.shape != (packed, packed):
            raise ValueError(
                f"h2 must be (norb, norb, norb, norb) or packed ({packed}, {packed}); got {h2a.shape}"
            )
        h2a = np.asarray(ao2mo.restore(1, h2a, norb), dtype=float)
    elif h2a.shape != (norb, norb, norb, norb):
        raise ValueError("h2 must be (norb, norb, norb, norb)")
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

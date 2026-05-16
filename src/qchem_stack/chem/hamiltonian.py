from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
from openfermion import (
    InteractionOperator,
    bravyi_kitaev,
    count_qubits,
    get_fermion_operator,
    jordan_wigner,
    symmetry_conserving_bravyi_kitaev,
)
from openfermion.chem.molecular_data import spinorb_from_spatial
from openfermion.linalg import get_sparse_operator
from openfermion.ops import QubitOperator

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.jordan_wigner_sparse import jordan_wigner_interaction_operator_sparse
from qchem_stack.chem.pauli_term_codec import canonical_pauli_string_from_term
from qchem_stack.chem.spatial_restricted_fermion import (
    restricted_spatial_integrals_to_fermion_operator,
)

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.restricted_integral_operator import (
        RestrictedActiveSpaceIntegralOperatorCompact,
    )

FermionQubitMappingName = Literal[
    "jordan_wigner",
    "bravyi_kitaev",
    "symmetry_conserving_bravyi_kitaev",
]


def _classical_driver_meta_payload(reference: Any) -> tuple[dict[str, Any], str]:
    if reference is None or not getattr(reference, "driver_meta", None):
        return {}, ""
    driver_meta = dict(reference.driver_meta)
    backend_tag = (
        str(
            driver_meta.get("upstream_classical_software_tag")
            or driver_meta.get("driver_family")
            or ""
        )
        .strip()
        .lower()
    )
    return driver_meta, backend_tag


def _resolve_integral_metadata(
    *,
    canonical_pack: CanonicalActiveSpaceIntegralPack | None,
    backend_tag: str,
    integral_source: str | None = None,
    integral_openfermion_bridge: str | None = None,
) -> tuple[str, str]:
    provenance = (
        dict(getattr(canonical_pack, "provenance", {}) or {})
        if canonical_pack is not None
        else {}
    )
    resolved_backend_tag = (
        str(backend_tag or provenance.get("classical_backend") or provenance.get("backend_id") or "")
        .strip()
        .lower()
    )
    explicit_source = str(integral_source or "").strip()
    explicit_bridge = str(integral_openfermion_bridge or "").strip()
    source = (
        explicit_source
        or str(provenance.get("upstream_integral_source") or "").strip()
        or (
            f"{resolved_backend_tag}_active_space"
            if resolved_backend_tag
            else "active_space_integrals"
        )
    )
    bridge = (
        explicit_bridge
        or str(
            provenance.get("integral_openfermion_bridge")
            or provenance.get("openfermion_bridge")
            or ""
        ).strip()
    )
    if not bridge:
        if resolved_backend_tag == "pyscf":
            bridge = "pyscf_tangelo_openfermion_v1"
        elif resolved_backend_tag:
            bridge = f"{resolved_backend_tag}_openfermion_interaction_operator_v1"
        else:
            bridge = "openfermion_interaction_operator_v1"
    return source, bridge


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
    if mapping == "bravyi_kitaev":
        return bravyi_kitaev(mol_op)
    if mapping == "symmetry_conserving_bravyi_kitaev":
        if n_spin_orbitals is None or n_active_fermions is None:
            raise ValueError(
                "symmetry_conserving_bravyi_kitaev requires n_spin_orbitals and n_active_fermions "
                "(OpenFermion SCBK removes two qubits vs JW on the same active space)."
            )
        fo = get_fermion_operator(mol_op)
        return symmetry_conserving_bravyi_kitaev(fo, int(n_spin_orbitals), int(n_active_fermions))
    raise ValueError(f"Unknown fermion_qubit_mapping: {mapping!r}")


def hamiltonian_fingerprint_from_qubit_operator(
    qop: QubitOperator,
    *,
    max_terms: int | None = None,
) -> tuple[str, bool]:
    """
    Deterministic SHA-256 digest (hex, first 32 chars) over sorted Pauli labels and coefficients.

    Identity term is labeled ``\"I\"``. Coefficients are serialized with ``:.16g``.
    If ``max_terms`` is set, only the first *max_terms* items after sorting are hashed
    and the second return value is ``True`` (truncated fingerprint).
    """
    rows: list[tuple[str, str]] = []
    for term, coeff in sorted(
        qop.terms.items(),
        key=lambda tv: (
            canonical_pauli_string_from_term(tv[0]),
            complex(tv[1]).real,
            complex(tv[1]).imag,
        ),
    ):
        label = canonical_pauli_string_from_term(term) if term else "I"
        z = complex(coeff)
        if abs(z.imag) <= 1e-14:
            rows.append((label, f"{z.real:.16g}"))
        else:
            rows.append((label, f"{z.real:.16g}{z.imag:+.16g}j"))
    truncated = False
    if max_terms is not None and len(rows) > max_terms:
        rows = rows[:max_terms]
        truncated = True
    payload = ";".join(f"{a}:{b}" for a, b in rows)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
    return digest, truncated


@dataclass
class QubitHamiltonian:
    """Qubit operator from a molecular :class:`InteractionOperator` + sparse cache.

    ``meta['fermion_to_qubit_map']`` records the mapping used (e.g. Jordan–Wigner, Bravyi–Kitaev, or SCBK).
    """

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

    if prefer_restricted_spatial_fermion_for_jordan_wigner:
        if fermion_qubit_mapping != "jordan_wigner":
            raise ValueError(
                "prefer_restricted_spatial_fermion_for_jordan_wigner requires fermion_qubit_mapping='jordan_wigner'."
            )
        if jordan_wigner_coeff_atol is not None:
            raise ValueError(
                "jordan_wigner_coeff_atol applies only to the InteractionOperator JW path; "
                "set prefer_restricted_spatial_fermion_for_jordan_wigner=False or atol=None."
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
    """Build active-space molecular Hamiltonian from backend-agnostic mean-field reference."""
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
    n_phys = int(count_qubits(qop))
    fp, fp_trunc = hamiltonian_fingerprint_from_qubit_operator(qop)
    driver_meta, backend_tag = _classical_driver_meta_payload(rhf)
    source_tag, bridge_tag = _resolve_integral_metadata(
        canonical_pack=canonical_pack,
        backend_tag=backend_tag,
        integral_source=integral_source,
        integral_openfermion_bridge=integral_openfermion_bridge,
    )
    meta: dict[str, Any] = {
        "fermion_to_qubit_map": fermion_qubit_mapping,
        "integral_source": source_tag,
        "integral_openfermion_bridge": bridge_tag,
        "jw_build": "interaction_operator",
        "n_active_orbitals": n_active_orbitals,
        "n_active_electrons": n_active_electrons,
        "n_qubits": n_phys,
        "hamiltonian_fingerprint": fp,
    }
    if fp_trunc:
        meta["hamiltonian_fingerprint_truncated"] = True
    if jordan_wigner_coeff_atol is not None:
        meta["jordan_wigner_coeff_atol"] = float(jordan_wigner_coeff_atol)
    if driver_meta:
        if backend_tag == "pyscf":
            meta["pyscf_driver"] = driver_meta
        else:
            meta["classical_driver"] = driver_meta
    if canonical_pack is not None:
        meta["canonical_integral_pack"] = {
            "schema": canonical_pack.schema,
            "provenance": dict(canonical_pack.provenance),
        }
    return QubitHamiltonian(
        operator=qop,
        n_qubits=n_phys,
        fermion_space=fermion_space,
        meta=meta,
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
    """Map compact MO integrals to qubits without instantiating a dense spin-orbital ERI tensor.

    Uses :func:`~qchem_stack.chem.spatial_restricted_fermion.restricted_spatial_integrals_to_fermion_operator`
    + OpenFermion JW **only** when ``fermion_qubit_mapping == \"jordan_wigner\"``. Other mappings fall back to
    :meth:`~qchem_stack.chem.restricted_integral_operator.RestrictedActiveSpaceIntegralOperatorCompact.to_interaction_operator`.
    """
    from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering

    if fermion_qubit_mapping != "jordan_wigner":
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
    qop = jordan_wigner(fo)
    n_phys = int(count_qubits(qop))
    fp, fp_trunc = hamiltonian_fingerprint_from_qubit_operator(qop)
    driver_meta, backend_tag = _classical_driver_meta_payload(rhf)
    source_tag, bridge_tag = _resolve_integral_metadata(
        canonical_pack=canonical_pack,
        backend_tag=backend_tag,
        integral_source=integral_source,
        integral_openfermion_bridge=integral_openfermion_bridge,
    )
    meta: dict[str, Any] = {
        "fermion_to_qubit_map": fermion_qubit_mapping,
        "integral_source": source_tag,
        "integral_openfermion_bridge": bridge_tag,
        "jw_build": "restricted_spatial_fermion_operator",
        "n_active_orbitals": n_active_orbitals,
        "n_active_electrons": n_active_electrons,
        "n_qubits": n_phys,
        "hamiltonian_fingerprint": fp,
    }
    if fp_trunc:
        meta["hamiltonian_fingerprint_truncated"] = True
    if driver_meta:
        if backend_tag == "pyscf":
            meta["pyscf_driver"] = driver_meta
        else:
            meta["classical_driver"] = driver_meta
    if canonical_pack is not None:
        meta["canonical_integral_pack"] = {
            "schema": canonical_pack.schema,
            "provenance": dict(canonical_pack.provenance),
        }
    return QubitHamiltonian(
        operator=qop,
        n_qubits=n_phys,
        fermion_space=fermion_space,
        meta=meta,
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

    if (
        prefer_restricted_spatial_fermion_for_jordan_wigner
        and fermion_qubit_mapping == "jordan_wigner"
    ):
        if jordan_wigner_coeff_atol is not None:
            raise ValueError(
                "jordan_wigner_coeff_atol applies only to the InteractionOperator JW path; "
                "set prefer_restricted_spatial_fermion_for_jordan_wigner=False or atol=None."
            )
        fo = restricted_spatial_integrals_to_fermion_operator(float(constant), h1a, h2a)
        qop = jordan_wigner(fo)
        jw_build = "restricted_spatial_fermion_operator"
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
        jw_build = "interaction_operator"
    n_phys = int(count_qubits(qop))
    fs = FermionSpace(n_spin_orbitals=n_spin, n_electrons=n_electrons)
    fp, fp_trunc = hamiltonian_fingerprint_from_qubit_operator(qop)
    meta: dict[str, Any] = {
        "fermion_to_qubit_map": fermion_qubit_mapping,
        "integral_source": integral_source,
        "integral_openfermion_bridge": "pyscf_tangelo_openfermion_v1",
        "jw_build": jw_build,
        "n_active_orbitals": norb,
        "n_active_electrons": n_electrons,
        "n_qubits": n_phys,
        "hamiltonian_fingerprint": fp,
    }
    if jordan_wigner_coeff_atol is not None:
        meta["jordan_wigner_coeff_atol"] = float(jordan_wigner_coeff_atol)
    if fp_trunc:
        meta["hamiltonian_fingerprint_truncated"] = True
    if pyscf_driver_meta:
        meta["pyscf_driver"] = dict(pyscf_driver_meta)
    if meta_extra:
        meta.update(meta_extra)
    return QubitHamiltonian(operator=qop, n_qubits=n_phys, fermion_space=fs, meta=meta)

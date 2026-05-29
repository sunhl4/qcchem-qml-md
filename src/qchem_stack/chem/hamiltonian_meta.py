"""Hamiltonian meta and fingerprint helpers (chem layer). Do not import orchestration."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Any, Literal

from qchem_stack.chem.bridges.driver_meta import fork_driver_meta
from qchem_stack.chem.pauli_term_codec import canonical_pauli_string_from_term
from qchem_stack.contracts.schema_ids import PYSCF_SPATIAL_OPENFERMION_BRIDGE_V1

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference

FermionQubitMappingName = Literal[
    "jordan_wigner",
    "bravyi_kitaev",
    "symmetry_conserving_bravyi_kitaev",
    "jkmn",
    "hard_core_boson",
]


def _attach_reference_energy_meta(
    meta: dict[str, Any], rhf: ClassicalMeanFieldReference | None
) -> None:
    if rhf is None:
        return
    meta["scf_energy_au"] = float(rhf.e_tot)
    meta["reference_energy_au"] = float(rhf.e_tot)


def _classical_driver_meta_payload(reference: Any) -> tuple[dict[str, Any], str]:
    if reference is None or not getattr(reference, "driver_meta", None):
        return {}, ""
    driver_meta = fork_driver_meta(reference.driver_meta)
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
        dict(getattr(canonical_pack, "provenance", {}) or {}) if canonical_pack is not None else {}
    )
    resolved_backend_tag = (
        str(
            backend_tag or provenance.get("classical_backend") or provenance.get("backend_id") or ""
        )
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
            bridge = PYSCF_SPATIAL_OPENFERMION_BRIDGE_V1
        elif resolved_backend_tag:
            bridge = f"{resolved_backend_tag}_openfermion_interaction_operator_v1"
        else:
            bridge = "openfermion_interaction_operator_v1"
    return source, bridge


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

"""Backend-agnostic active-space integral interchange (after mean-field).

The compact MO blocks are the same representation used on the PySCF CASCI ``get_h1eff`` /
``get_h2eff`` path; other classical backends can populate the same object when available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from qchem_stack.chem.restricted_integral_operator import (
    RestrictedActiveSpaceIntegralOperatorCompact,
)

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.drivers.pyscf_driver import PySCFRHFResult


SCHEMA_V1 = "qchem_canonical_active_space_integral_pack_v1"


@dataclass(frozen=True)
class CanonicalActiveSpaceIntegralPack:
    """Restricted active-space MO integrals + provenance for qubit Hamiltonian construction."""

    compact: RestrictedActiveSpaceIntegralOperatorCompact
    provenance: dict[str, Any] = field(default_factory=dict)

    @property
    def schema(self) -> str:
        return SCHEMA_V1

    @classmethod
    def from_pyscf_reference(
        cls,
        rhf: PySCFRHFResult,
        *,
        n_active_orbitals: int,
        n_active_electrons: int,
    ) -> CanonicalActiveSpaceIntegralPack:
        from qchem_stack.chem.drivers.pyscf_driver import unwrap_pyscf_rhf_for_backend_operations

        ref = unwrap_pyscf_rhf_for_backend_operations(rhf)
        compact = RestrictedActiveSpaceIntegralOperatorCompact.from_pyscf_rhf(
            ref,
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
        )
        prov: dict[str, Any] = {
            "pack_schema": SCHEMA_V1,
            "upstream_integral_source": "pyscf_casci_h2eff_compact",
            "integral_openfermion_bridge": "pyscf_tangelo_openfermion_v1",
            "classical_backend": "pyscf",
        }
        dm = getattr(rhf, "driver_meta", None) or {}
        if dm:
            prov["classical_reference_meta"] = dict(dm)
        return cls(compact=compact, provenance=prov)

    @classmethod
    def from_classical_reference(
        cls,
        reference: ClassicalMeanFieldReference,
        *,
        n_active_orbitals: int,
        n_active_electrons: int,
    ) -> CanonicalActiveSpaceIntegralPack:
        """Build canonical pack from a backend-agnostic mean-field reference.

        This is the preferred entry for downstream code. Backend-specific builders
        stay encapsulated here so pipeline/algorithms do not branch on driver names.
        """
        tag = reference.backend_tag()
        if tag == "pyscf":
            return cls.from_pyscf_reference(
                reference.as_pyscf_rhf_result(),
                n_active_orbitals=n_active_orbitals,
                n_active_electrons=n_active_electrons,
            )
        raise NotImplementedError(
            "CanonicalActiveSpaceIntegralPack.from_classical_reference has no integral builder "
            f"for backend {tag!r} yet. Implement backend-specific active-space integral export "
            "and route it through this method."
        )

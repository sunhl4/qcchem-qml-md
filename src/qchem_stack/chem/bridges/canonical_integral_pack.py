"""Backend-agnostic active-space integral interchange (after mean-field).

The compact MO blocks are the same representation used on the PySCF CASCI ``get_h1eff`` /
``get_h2eff`` path; other classical backends can populate the same object when available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from qchem_stack.chem.bridges.driver_meta import fork_driver_meta
from qchem_stack.chem.restricted_integral_operator import (
    RestrictedActiveSpaceIntegralOperatorCompact,
)
from qchem_stack.contracts.schema_ids import PYSCF_SPATIAL_OPENFERMION_BRIDGE_V1

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.drivers.pyscf_driver_types import PySCFRHFResult


SCHEMA_V1 = "qchem_canonical_active_space_integral_pack_v1"


def _pack_provenance(
    *,
    classical_backend: str,
    upstream_integral_source: str,
    integral_openfermion_bridge: str,
    driver_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "pack_schema": SCHEMA_V1,
        "upstream_integral_source": upstream_integral_source,
        "integral_openfermion_bridge": integral_openfermion_bridge,
        "classical_backend": classical_backend,
    }
    if driver_meta:
        out["classical_reference_meta"] = fork_driver_meta(driver_meta)
    return out


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
        from qchem_stack.chem.drivers.pyscf_driver_types import (
            unwrap_pyscf_rhf_for_backend_operations,
        )

        ref = unwrap_pyscf_rhf_for_backend_operations(rhf)
        compact = RestrictedActiveSpaceIntegralOperatorCompact.from_pyscf_rhf(
            ref,
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
        )
        prov = _pack_provenance(
            classical_backend="pyscf",
            upstream_integral_source="pyscf_casci_h2eff_compact",
            integral_openfermion_bridge=PYSCF_SPATIAL_OPENFERMION_BRIDGE_V1,
            driver_meta=getattr(rhf, "driver_meta", None) or {},
        )
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
        from qchem_stack.chem.integrals.exporter_registry import get_active_space_integral_exporter

        tag = reference.backend_tag()
        exporter = get_active_space_integral_exporter(tag)
        return exporter.build_canonical_pack(
            reference,
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
        )

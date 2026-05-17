"""PySCF CASCI active-space integral export."""

from __future__ import annotations

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.integrals.exporter_protocol import ActiveSpaceIntegralExporter


class PySCFActiveSpaceIntegralExporter(ActiveSpaceIntegralExporter):
    backend_tag = "pyscf"

    def build_canonical_pack(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        n_active_orbitals: int,
        n_active_electrons: int,
    ) -> CanonicalActiveSpaceIntegralPack:
        if reference.backend_tag() != "pyscf":
            raise ValueError(
                f"PySCFActiveSpaceIntegralExporter expected backend_tag='pyscf', "
                f"got {reference.backend_tag()!r}."
            )
        return CanonicalActiveSpaceIntegralPack.from_pyscf_reference(
            reference.as_pyscf_rhf_result(),
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
        )

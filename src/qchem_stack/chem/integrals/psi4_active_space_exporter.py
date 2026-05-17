"""Psi4 active-space integral export."""

from __future__ import annotations

import numpy as np

from qchem_stack.chem.bridges.canonical_integral_pack import (
    SCHEMA_V1,
    CanonicalActiveSpaceIntegralPack,
)
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.integrals.exporter_protocol import ActiveSpaceIntegralExporter
from qchem_stack.chem.integrals.psi4_active_space import active_space_casci_raw_blocks_psi4
from qchem_stack.chem.restricted_integral_operator import (
    RestrictedActiveSpaceIntegralOperatorCompact,
)


class Psi4ActiveSpaceIntegralExporter(ActiveSpaceIntegralExporter):
    backend_tag = "psi4"

    def build_canonical_pack(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        n_active_orbitals: int,
        n_active_electrons: int,
    ) -> CanonicalActiveSpaceIntegralPack:
        if reference.backend_tag() != "psi4":
            raise ValueError(
                f"Psi4ActiveSpaceIntegralExporter expected backend_tag='psi4', "
                f"got {reference.backend_tag()!r}."
            )
        constant, h1, h2 = active_space_casci_raw_blocks_psi4(
            reference,
            n_active_orbitals,
            n_active_electrons,
        )
        compact = RestrictedActiveSpaceIntegralOperatorCompact(
            constant=float(constant),
            h1_active_mo=np.asarray(h1, dtype=float),
            eri_active_mo_compact=np.asarray(h2, dtype=float),
            n_active_orbitals=int(n_active_orbitals),
            n_active_electrons=int(n_active_electrons),
            symmetry_meta={"psi4_symmetry": "c1_assumed"},
            storage_schema="psi4_casci_mo_dense_v1",
        )
        prov = {
            "pack_schema": SCHEMA_V1,
            "upstream_integral_source": "psi4_casci_mo_compact",
            "integral_openfermion_bridge": "psi4_mo_to_openfermion_v1",
            "classical_backend": "psi4",
        }
        dm = dict(reference.driver_meta or {})
        if dm:
            prov["classical_reference_meta"] = dm
        return CanonicalActiveSpaceIntegralPack(compact=compact, provenance=prov)

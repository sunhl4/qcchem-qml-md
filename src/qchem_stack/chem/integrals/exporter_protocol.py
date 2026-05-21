"""Backend-specific active-space integral export protocols."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference


@runtime_checkable
class ActiveSpaceIntegralExporter(Protocol):
    """Build :class:`CanonicalActiveSpaceIntegralPack` from a mean-field reference."""

    backend_tag: str

    def build_canonical_pack(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        n_active_orbitals: int,
        n_active_electrons: int,
    ) -> CanonicalActiveSpaceIntegralPack: ...

"""Active-space hook protocol shared by backend adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


@runtime_checkable
class ActiveSpaceBackendHooks(Protocol):
    def apply_avas(self, cfg: ExperimentConfig, reference: ClassicalMeanFieldReference) -> None: ...

    def casscf_energy_and_maybe_orbitals(
        self,
        cfg: ExperimentConfig,
        reference: ClassicalMeanFieldReference,
        *,
        update_integrals_orbitals: bool,
        record_audit: bool,
    ) -> None: ...

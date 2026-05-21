"""PySCF :class:`ActiveSpaceBackendHooks` adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.active_space.avas_projection import apply_avas_projection
from qchem_stack.chem.active_space.pyscf_active_space_hooks import (
    casscf_energy_and_maybe_orbitals as _casscf_pyscf,
)

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


class PySCFActiveSpaceHooks:
    def apply_avas(self, cfg: ExperimentConfig, reference: ClassicalMeanFieldReference) -> None:
        apply_avas_projection(cfg, reference)

    def casscf_energy_and_maybe_orbitals(
        self,
        cfg: ExperimentConfig,
        reference: ClassicalMeanFieldReference,
        *,
        update_integrals_orbitals: bool,
        record_audit: bool,
    ) -> None:
        _casscf_pyscf(
            cfg,
            reference,
            update_integrals_orbitals=update_integrals_orbitals,
            record_audit=record_audit,
        )

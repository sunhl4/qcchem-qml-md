"""Dispatch active-space hooks (AVAS, CASSCF) by classical backend."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.active_space.hooks_protocol import ActiveSpaceBackendHooks
from qchem_stack.chem.active_space.hooks_registry import get_active_space_hooks

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig

__all__ = [
    "ActiveSpaceBackendHooks",
    "apply_avas_to_reference",
    "casscf_orbital_pass",
    "get_active_space_hooks",
    "patch_experiment_active_space_resolution",
]


def apply_avas_to_reference(cfg: ExperimentConfig, reference: ClassicalMeanFieldReference) -> None:
    hooks = get_active_space_hooks(reference.backend_tag())
    hooks.apply_avas(cfg, reference)


def casscf_orbital_pass(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    update_integrals_orbitals: bool,
    record_audit: bool,
) -> None:
    hooks = get_active_space_hooks(reference.backend_tag())
    hooks.casscf_energy_and_maybe_orbitals(
        cfg,
        reference,
        update_integrals_orbitals=update_integrals_orbitals,
        record_audit=record_audit,
    )


def patch_experiment_active_space_resolution(
    cfg: ExperimentConfig, reference: ClassicalMeanFieldReference
) -> ExperimentConfig:
    from qchem_stack.chem.active_space.resolution import (
        patch_experiment_active_space_resolution as _patch,
    )

    return _patch(cfg, reference)

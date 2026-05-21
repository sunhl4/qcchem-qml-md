"""Dispatch active-space hooks (AVAS, CASSCF) by classical backend."""

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


def get_active_space_hooks(backend_tag: str) -> ActiveSpaceBackendHooks:
    tag = str(backend_tag).strip().lower()
    if tag == "pyscf":
        from qchem_stack.chem.active_space.pyscf_hooks_adapter import PySCFActiveSpaceHooks

        return PySCFActiveSpaceHooks()
    if tag == "psi4":
        from qchem_stack.chem.active_space.psi4_active_space_hooks import Psi4ActiveSpaceHooks

        return Psi4ActiveSpaceHooks()
    raise ValueError(f"No ActiveSpaceBackendHooks for backend {tag!r}.")


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
    from qchem_stack.chem.active_space.pyscf_active_space_hooks import (
        patch_experiment_active_space_resolution as _patch,
    )

    return _patch(cfg, reference)

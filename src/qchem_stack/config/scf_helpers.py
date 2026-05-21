"""Read-only helpers for :class:`~qchem_stack.config.scf.SCFSpec`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .scf import SCFSpec
    from .scf_specs import ScfDriverControlsSpec


def resolve_scf_driver_controls(spec: SCFSpec) -> ScfDriverControlsSpec:
    driver = str(spec.driver).strip().lower()
    if driver == "psi4":
        return spec.psi4
    return spec.pyscf


def resolve_scf_max_cycle(spec: SCFSpec) -> int | None:
    return resolve_scf_driver_controls(spec).max_cycle


def resolve_scf_chkfile(spec: SCFSpec) -> str | None:
    return resolve_scf_driver_controls(spec).chkfile


def resolve_scf_init_guess(spec: SCFSpec) -> str | None:
    return resolve_scf_driver_controls(spec).init_guess


def resolve_scf_level_shift(spec: SCFSpec) -> float | None:
    return resolve_scf_driver_controls(spec).level_shift


def resolve_scf_use_newton(spec: SCFSpec) -> bool:
    return bool(resolve_scf_driver_controls(spec).use_newton)


def resolve_scf_diis_space_dimension(spec: SCFSpec) -> int | None:
    return resolve_scf_driver_controls(spec).diis_space_dimension


def resolve_scf_density_fit(spec: SCFSpec) -> bool:
    return bool(resolve_scf_driver_controls(spec).density_fit)


def resolve_scf_density_fit_auxbasis(spec: SCFSpec) -> str | None:
    return resolve_scf_driver_controls(spec).density_fit_auxbasis

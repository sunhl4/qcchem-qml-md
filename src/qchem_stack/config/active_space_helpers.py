"""Read-only helpers for :class:`~qchem_stack.config.active_space.ActiveSpaceSpec`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .active_space import ActiveSpaceSpec

if TYPE_CHECKING:
    from .active_space_mapping_specs import FermionQubitMappingName

__all__ = [
    "ActiveSpaceSpec",
    "resolve_fermion_qubit_mapping",
    "resolve_n_electrons",
    "resolve_n_orbitals",
]


def resolve_n_orbitals(spec: ActiveSpaceSpec) -> int:
    """Active spatial orbital count."""
    v = spec.manual.n_orbitals if spec.strategy == "manual" else spec.cas.n_orbitals
    if v is None:
        raise ValueError("active_space: n_orbitals is unset.")
    return int(v)


def resolve_n_electrons(spec: ActiveSpaceSpec) -> int:
    """Active electron count."""
    v = spec.manual.n_electrons if spec.strategy == "manual" else spec.cas.n_electrons
    if v is None:
        raise ValueError("active_space: n_electrons is unset.")
    return int(v)


def resolve_fermion_qubit_mapping(spec: ActiveSpaceSpec) -> FermionQubitMappingName:
    return spec.mapping.fermion_qubit

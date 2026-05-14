"""Cross-field validation helpers for :mod:`qchem_stack.config.active_space`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .active_space import ActiveSpaceSpec


CAS_LIKE_STRATEGIES = ("cas", "avas_stub", "avas")


def validate_frozen_orbitals(values: list[int]) -> list[int]:
    if any(index < 0 for index in values):
        raise ValueError("active_space.frozen_orbitals entries must be >= 0.")
    if len(set(values)) != len(values):
        raise ValueError("active_space.frozen_orbitals must not contain duplicates.")
    return list(values)


def normalize_active_space_entry(spec: ActiveSpaceSpec) -> None:
    if spec.strategy in CAS_LIKE_STRATEGIES:
        _normalize_cas_like_strategy(spec)
        return
    _normalize_manual_strategy(spec)


def _normalize_cas_like_strategy(spec: ActiveSpaceSpec) -> None:
    if (
        spec.ncas is not None
        and spec.n_active_orbitals is not None
        and int(spec.ncas) != int(spec.n_active_orbitals)
    ):
        raise ValueError(
            "active_space.ncas and n_active_orbitals disagree for CAS-like strategies "
            "('cas', 'avas_stub', 'avas')."
        )
    if (
        spec.nelecas is not None
        and spec.n_active_electrons is not None
        and int(spec.nelecas) != int(spec.n_active_electrons)
    ):
        raise ValueError(
            "active_space.nelecas and n_active_electrons disagree for CAS-like strategies "
            "('cas', 'avas_stub', 'avas')."
        )
    ncas = spec.ncas if spec.ncas is not None else spec.n_active_orbitals
    nelecas = spec.nelecas if spec.nelecas is not None else spec.n_active_electrons
    if ncas is None or nelecas is None:
        raise ValueError(
            "active_space.strategy in {'cas','avas_stub','avas'} requires ncas/nelecas "
            "(or legacy n_active_orbitals/n_active_electrons)."
        )
    if int(ncas) < 1 or int(nelecas) < 1:
        raise ValueError("active_space ncas/nelecas must both be >= 1.")
    spec.ncas = int(ncas)
    spec.nelecas = int(nelecas)
    spec.n_active_orbitals = int(ncas)
    spec.n_active_electrons = int(nelecas)


def _normalize_manual_strategy(spec: ActiveSpaceSpec) -> None:
    if spec.n_active_orbitals is None or spec.n_active_electrons is None:
        raise ValueError(
            "active_space.strategy='manual' requires n_active_orbitals and n_active_electrons."
        )
    if int(spec.n_active_orbitals) < 1 or int(spec.n_active_electrons) < 1:
        raise ValueError("active_space n_active_orbitals/n_active_electrons must both be >= 1.")
    if spec.ncas is not None and int(spec.ncas) != int(spec.n_active_orbitals):
        raise ValueError("active_space.ncas must equal n_active_orbitals when strategy='manual'.")
    if spec.nelecas is not None and int(spec.nelecas) != int(spec.n_active_electrons):
        raise ValueError(
            "active_space.nelecas must equal n_active_electrons when strategy='manual'."
        )
    spec.n_active_orbitals = int(spec.n_active_orbitals)
    spec.n_active_electrons = int(spec.n_active_electrons)
    spec.ncas = int(spec.n_active_orbitals)
    spec.nelecas = int(spec.n_active_electrons)


def validate_jw_optimizer_flags(spec: ActiveSpaceSpec) -> None:
    if spec.prefer_restricted_spatial_fermion_for_jordan_wigner:
        if spec.fermion_qubit_mapping != "jordan_wigner":
            raise ValueError(
                "active_space.prefer_restricted_spatial_fermion_for_jordan_wigner requires "
                "active_space.fermion_qubit_mapping='jordan_wigner'."
            )
        if spec.jordan_wigner_coeff_atol is not None:
            raise ValueError(
                "active_space.jordan_wigner_coeff_atol cannot be set when "
                "prefer_restricted_spatial_fermion_for_jordan_wigner is True."
            )
    if spec.jordan_wigner_coeff_atol is not None and float(spec.jordan_wigner_coeff_atol) <= 0:
        raise ValueError("active_space.jordan_wigner_coeff_atol must be positive when set.")

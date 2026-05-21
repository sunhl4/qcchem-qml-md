"""Cross-field validation helpers for :mod:`qchem_stack.config.active_space`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .active_space import ActiveSpaceSpec

CAS_LIKE_STRATEGIES = ("cas", "avas_stub", "avas")


def validate_frozen_orbitals(values: list[int]) -> list[int]:
    if any(index < 0 for index in values):
        raise ValueError("active_space.manual.frozen_orbitals entries must be >= 0.")
    if len(set(values)) != len(values):
        raise ValueError("active_space.manual.frozen_orbitals must not contain duplicates.")
    return list(values)


def normalize_active_space_entry(spec: ActiveSpaceSpec) -> None:
    if spec.strategy in CAS_LIKE_STRATEGIES:
        _normalize_cas_like_strategy(spec)
    else:
        _normalize_manual_strategy(spec)
    validate_active_space_post_normalize(spec)


def validate_active_space_post_normalize(spec: ActiveSpaceSpec) -> None:
    n_orb = spec.cas.n_orbitals
    n_el = spec.cas.n_electrons
    if n_orb is None or n_el is None:
        raise ValueError(
            "active_space.cas: n_orbitals and n_electrons must be set "
            f"(got n_orbitals={n_orb!r}, n_electrons={n_el!r})."
        )
    if int(n_el) > 2 * int(n_orb):
        raise ValueError(
            f"active_space.cas: n_electrons ({n_el}) cannot exceed 2*n_orbitals ({2 * int(n_orb)})."
        )
    if spec.manual.frozen_orbitals and spec.strategy != "manual":
        raise ValueError(
            "active_space: manual.frozen_orbitals is only used when strategy='manual'; "
            f"got strategy={spec.strategy!r} with frozen_orbitals={list(spec.manual.frozen_orbitals)!r}. "
            "Remove frozen_orbitals or set strategy: manual."
        )


def _assign_active_space_counts(
    spec: ActiveSpaceSpec, *, n_orbitals: int, n_electrons: int
) -> None:
    no = int(n_orbitals)
    ne = int(n_electrons)
    spec.cas.n_orbitals = no
    spec.cas.n_electrons = ne
    if spec.strategy == "manual":
        spec.manual.n_orbitals = no
        spec.manual.n_electrons = ne


def _normalize_cas_like_strategy(spec: ActiveSpaceSpec) -> None:
    block = spec.cas
    n_orbitals = block.n_orbitals
    n_electrons = block.n_electrons
    if n_orbitals is None or n_electrons is None:
        raise ValueError(
            "active_space: strategy in {'cas','avas_stub','avas'} requires "
            "cas.n_orbitals and cas.n_electrons."
        )
    if int(n_orbitals) < 1 or int(n_electrons) < 1:
        raise ValueError("active_space.cas: n_orbitals and n_electrons must both be >= 1.")
    _assign_active_space_counts(spec, n_orbitals=int(n_orbitals), n_electrons=int(n_electrons))


def _normalize_manual_strategy(spec: ActiveSpaceSpec) -> None:
    block = spec.manual
    n_orbitals = block.n_orbitals
    n_electrons = block.n_electrons
    if n_orbitals is None or n_electrons is None:
        raise ValueError(
            "active_space: strategy='manual' requires manual.n_orbitals and manual.n_electrons."
        )
    if int(n_orbitals) < 1 or int(n_electrons) < 1:
        raise ValueError("active_space.manual: n_orbitals and n_electrons must both be >= 1.")
    _assign_active_space_counts(spec, n_orbitals=int(n_orbitals), n_electrons=int(n_electrons))


def validate_jw_optimizer_flags(spec: ActiveSpaceSpec) -> None:
    jw = spec.jw
    mapping = spec.mapping.fermion_qubit
    if jw.prefer_restricted_spatial:
        if mapping != "jordan_wigner":
            raise ValueError(
                "active_space.jw.prefer_restricted_spatial requires "
                "active_space.mapping.fermion_qubit='jordan_wigner'."
            )
        if jw.coeff_atol is not None:
            raise ValueError(
                "active_space.jw.coeff_atol cannot be set when prefer_restricted_spatial is True."
            )
    if jw.coeff_atol is not None:
        if mapping != "jordan_wigner":
            raise ValueError(
                "active_space.jw.coeff_atol applies only when mapping.fermion_qubit='jordan_wigner' "
                f"(got {mapping!r})."
            )
        if float(jw.coeff_atol) <= 0:
            raise ValueError("active_space.jw.coeff_atol must be positive when set.")

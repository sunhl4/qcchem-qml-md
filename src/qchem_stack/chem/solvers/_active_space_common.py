"""Shared active-space helpers for classical integral solvers."""

from __future__ import annotations

from typing import Any


def resolve_active_space_spec(kwargs: dict[str, Any]) -> tuple[int, int]:
    ncas_raw = kwargs.get("n_active_orbitals", kwargs.get("ncas"))
    nele_raw = kwargs.get("n_active_electrons", kwargs.get("nelecas"))
    if ncas_raw is None or nele_raw is None:
        raise ValueError(
            "get_integrals requires n_active_orbitals/n_active_electrons (aliases: ncas/nelecas)."
        )
    ncas = int(ncas_raw)
    nelecas = int(nele_raw)
    if ncas <= 0 or nelecas <= 0:
        raise ValueError("n_active_orbitals and n_active_electrons must be positive integers.")
    return ncas, nelecas

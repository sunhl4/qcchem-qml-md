"""Frozen-core / CASCI core orbital counts shared across backends."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def casci_ncore_spatial(
    cfg: ExperimentConfig,
    *,
    n_mo: int,
    n_active_electrons: int,
    n_active_orbitals: int,
) -> int:
    """Return number of frozen spatial core orbitals before the active window.

    Matches PySCF ``CASCI.ncore`` for closed-shell RHF when ``manual`` frozen
    orbitals are not used: ``(nelec - n_active) // 2``.
    """
    if cfg.active_space.strategy == "manual" and cfg.active_space.manual.frozen_orbitals:
        return len(cfg.active_space.manual.frozen_orbitals)
    ne = int(n_active_electrons)
    ncas = int(n_active_orbitals)
    if ne % 2 != 0:
        raise ValueError("casci_ncore_spatial requires even active electron count (RHF).")
    ncore = (ne - ncas) // 2
    if ncore < 0 or ncore + ncas > int(n_mo):
        raise ValueError(
            f"Invalid CASCI core window: ncore={ncore}, ncas={ncas}, n_mo={n_mo}, nelec={ne}."
        )
    return int(ncore)

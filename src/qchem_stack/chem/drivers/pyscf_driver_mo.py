"""MO manipulation and active-space sizing helpers for PySCF driver workflows."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver


def classify_mean_field_spin_symmetry(mf: object) -> Literal["RHF", "ROHF", "UHF"]:
    from pyscf import scf as scf_mod

    if isinstance(mf, scf_mod.uhf.UHF):
        return "UHF"
    if isinstance(mf, scf_mod.rohf.ROHF):
        return "ROHF"
    return "RHF"


def reorder_molecular_orbitals_columns(mo_coeff: np.ndarray, column_order: list[int]) -> np.ndarray:
    m = np.asarray(mo_coeff, dtype=float)
    perm = list(column_order)
    if sorted(perm) != list(range(m.shape[1])):
        raise ValueError("column_order must be a permutation of range(n_molecular_orbitals).")
    return np.asarray(m[:, perm], dtype=float)


def make_actives_contiguous_columns(
    mo_coeff: np.ndarray,
    active_molecular_orbital_indices: list[int],
    *,
    frozen_prefix_count: int = 0,
) -> tuple[np.ndarray, list[int]]:
    m = np.asarray(mo_coeff, dtype=float)
    nmo = int(m.shape[1])
    frozen_prefix_count = int(max(0, frozen_prefix_count))
    if frozen_prefix_count > nmo:
        raise ValueError("frozen_prefix_count exceeds MO dimension.")
    act = sorted({int(i) for i in active_molecular_orbital_indices})
    pool = list(range(nmo))
    inactive = [i for i in pool if i not in act]
    prefix = inactive[:frozen_prefix_count]
    rest_inactive = [i for i in inactive if i not in prefix]
    perm = prefix + act + rest_inactive
    if len(set(perm)) != nmo:
        raise ValueError("active indices overlap frozen prefix selections.")
    return reorder_molecular_orbitals_columns(m, perm), perm


def get_ncas_nelec_couplet(
    driver: PySCFDriver,
    *,
    resolved_reference: ClassicalMeanFieldReference | None = None,
) -> tuple[int, int]:
    from qchem_stack.chem.active_space.pyscf_active_space_hooks import (
        RESOLVED_ACTIVE_SPACE_META_KEY,
    )

    if resolved_reference is not None:
        blk = resolved_reference.driver_meta.get(RESOLVED_ACTIVE_SPACE_META_KEY)
        if isinstance(blk, dict) and blk.get("n_active_orbitals") is not None:
            return int(blk["n_active_orbitals"]), int(blk["n_active_electrons"])  # type: ignore[index]
    if driver.active_space is None:
        raise ValueError("active_space unavailable; construct PySCFDriver.from_config(...) first.")
    return int(driver.active_space.cas.n_orbitals), int(driver.active_space.cas.n_electrons)

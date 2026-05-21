"""Psi4 1.x reference helpers (RHF return type vs legacy Wavefunction API)."""

from __future__ import annotations

from typing import Any

import numpy as np


def unwrap_psi4_reference(ref: Any) -> Any:
    """Return raw Psi4 ``RHF`` / ``Wavefunction`` from adapters or wrappers."""
    mf = getattr(ref, "mf", ref)
    if hasattr(mf, "raw_handle") and callable(mf.raw_handle):
        return mf.raw_handle()
    return mf


def psi4_nao(wfn: Any) -> int:
    if hasattr(wfn, "nao") and callable(wfn.nao):
        return int(wfn.nao())  # type: ignore[arg-type]
    ca = np.asarray(wfn.Ca(), dtype=float)
    return int(ca.shape[0])


def psi4_nmo(wfn: Any) -> int:
    if hasattr(wfn, "nmo") and callable(wfn.nmo):
        return int(wfn.nmo())  # type: ignore[arg-type]
    ca = np.asarray(wfn.Ca(), dtype=float)
    return int(ca.shape[1])


def psi4_nirrep(wfn: Any) -> int:
    if hasattr(wfn, "nirrep") and callable(wfn.nirrep):
        return int(wfn.nirrep())  # type: ignore[arg-type]
    return 1


def psi4_mints_helper(wfn: Any) -> Any:
    """Build :class:`psi4.core.MintsHelper` for one- and two-electron AO integrals."""
    from psi4 import core

    if hasattr(wfn, "basisset") and callable(wfn.basisset):
        return core.MintsHelper(wfn.basisset())
    return core.MintsHelper(wfn)


def psi4_overlap_ao(wfn: Any) -> np.ndarray:
    if hasattr(wfn, "S") and callable(wfn.S):
        return np.asarray(wfn.S(), dtype=float)
    mints = psi4_mints_helper(wfn)
    if hasattr(mints, "ao_overlap"):
        return np.asarray(mints.ao_overlap(), dtype=float)
    return np.asarray(mints.S(), dtype=float)


def psi4_hcore_ao(wfn: Any) -> np.ndarray:
    mints = psi4_mints_helper(wfn)
    if hasattr(mints, "ao_kinetic") and hasattr(mints, "ao_potential"):
        t = np.asarray(mints.ao_kinetic(), dtype=float)
        v = np.asarray(mints.ao_potential(), dtype=float)
        return t + v
    if hasattr(mints, "T") and hasattr(mints, "V"):
        return np.asarray(mints.T(), dtype=float) + np.asarray(mints.V(), dtype=float)
    raise AttributeError("Psi4 MintsHelper lacks ao_kinetic/ao_potential and T/V.")


def psi4_ao_eri_chemist(wfn: Any) -> np.ndarray:
    mints = psi4_mints_helper(wfn)
    return np.asarray(mints.ao_eri(), dtype=float)


def psi4_aoslice_by_atom(wfn: Any) -> list[tuple[int, int]]:
    """Return half-open AO index ranges per atom (contiguous blocks in Psi4 ordering)."""
    bs = wfn.basisset()
    nao = int(bs.nao())
    nat = int(wfn.molecule().natom())
    per_atom: list[list[int]] = [[] for _ in range(nat)]
    for i in range(nao):
        c = int(bs.function_to_center(i))
        if c < 0 or c >= nat:
            raise ValueError(f"Psi4 AO {i} maps to invalid center {c} (n_atom={nat}).")
        per_atom[c].append(i)
    ranges: list[tuple[int, int]] = []
    for atom_idx, idxs in enumerate(per_atom):
        if not idxs:
            raise ValueError(f"Psi4 basis has no AO functions on atom index {atom_idx}.")
        p0, p1 = min(idxs), max(idxs) + 1
        if idxs != list(range(p0, p1)):
            raise ValueError(
                "Psi4 AO indices on an atom are not contiguous; "
                "extend fragment_ao_indices for non-contiguous layouts."
            )
        ranges.append((p0, p1))
    return ranges


def psi4_matrix_from_numpy(arr: np.ndarray) -> Any:
    from psi4 import core

    return core.Matrix.from_array(np.asarray(arr, dtype=float))


def psi4_set_ca(wfn: Any, mo_ao: np.ndarray) -> None:
    """Assign RHF alpha MO coefficients from a NumPy array."""
    wfn.Ca().copy(psi4_matrix_from_numpy(mo_ao))


def psi4_fock_ao(wfn: Any, *, density_ao: np.ndarray | None = None) -> np.ndarray:
    if density_ao is None and hasattr(wfn, "Fa") and callable(wfn.Fa):
        return np.asarray(wfn.Fa(), dtype=float)
    dm = np.asarray(density_ao if density_ao is not None else wfn.Da(), dtype=float)
    mints = psi4_mints_helper(wfn)
    if hasattr(mints, "ao_fock"):
        return np.asarray(mints.ao_fock(psi4_matrix_from_numpy(dm)), dtype=float)
    hcore = psi4_hcore_ao(wfn)
    eri = psi4_ao_eri_chemist(wfn)
    j = np.einsum("pqrs,rs->pq", eri, dm, optimize=True)
    k = np.einsum("pqrs,sr->pq", eri, dm, optimize=True)
    return np.asarray(hcore + 2.0 * j - k, dtype=float)

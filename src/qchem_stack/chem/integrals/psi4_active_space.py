"""Psi4 CASCI-style active-space MO integrals (RHF reference, closed-shell).

Tested in CI (optional ``pytest -m psi4``) against PySCF H2 sto-3g with soft thresholds in
``tests/test_psi4_pyscf_h2_canonical_parity.py`` (``PSI4_PYSCF_H2_CONSTANT_ATOL=5e-3``,
``PSI4_PYSCF_H2_H1_MAX_ABS_ATOL=5e-2``, ``PSI4_PYSCF_H2_H2_MAX_ABS_ATOL=8e-2``). Psi4 API varies by release; record
``psi4.__version__`` in ``driver_meta`` when debugging mismatches.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _unwrap_psi4_wfn(ref: Any) -> Any:
    mf = getattr(ref, "mf", ref)
    if hasattr(mf, "raw_handle"):
        return mf.raw_handle()
    return mf


def _casci_effective_blocks_from_mo_integrals(
    *,
    h_core_mo: np.ndarray,
    eri_mo_chemist: np.ndarray,
    enuc: float,
    n_core_pairs: int,
    active_start: int,
    n_active_orbitals: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Build CASCI-style ``(constant, h1_eff, h2_active)`` from MO chemist integrals."""
    hmo = np.asarray(h_core_mo, dtype=float)
    eri = np.asarray(eri_mo_chemist, dtype=float)
    nmo = int(hmo.shape[0])
    if hmo.shape != (nmo, nmo):
        raise ValueError("h_core_mo must be square.")
    if eri.shape != (nmo, nmo, nmo, nmo):
        raise ValueError("eri_mo_chemist must be (nmo, nmo, nmo, nmo).")

    start = int(active_start)
    stop = start + int(n_active_orbitals)
    if start < 0 or stop > nmo:
        raise ValueError("active window out of range for MO basis.")
    if n_core_pairs < 0 or int(n_core_pairs) > start:
        raise ValueError("invalid n_core_pairs for active window.")

    h1 = np.asarray(hmo[start:stop, start:stop], dtype=float)
    h2 = np.asarray(eri[start:stop, start:stop, start:stop, start:stop], dtype=float)

    n_core = int(n_core_pairs)
    if n_core == 0:
        return float(enuc), h1, h2

    c = slice(0, n_core)
    J_core = float(np.einsum("iijj->", eri[c, c, c, c], optimize=True))
    K_core = float(np.einsum("ijji->", eri[c, c, c, c], optimize=True))
    e_core_1e = 2.0 * float(np.trace(hmo[c, c]))
    constant = float(enuc) + e_core_1e + 2.0 * J_core - K_core

    a = slice(start, stop)
    j_act = np.asarray(np.einsum("uvii->uv", eri[a, a, c, c], optimize=True), dtype=float)
    k_act = np.asarray(np.einsum("uiiv->uv", eri[a, c, c, a], optimize=True), dtype=float)
    h1_eff = h1 + 2.0 * j_act - k_act
    return float(constant), h1_eff, h2


def active_space_casci_raw_blocks_psi4(
    ref_wfn: Any,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return ``(constant, h1_active, h2_active)`` in chemists' MO layout.

    Uses Psi4 ``energy('casci')`` at fixed RHF orbitals, then reads the CASCI
    Hamiltonian from the returned wavefunction when available; otherwise builds
  MO integrals via :class:`psi4.core.MintsHelper` on the active subspace.
    """
    wfn = _unwrap_psi4_wfn(ref_wfn)
    import psi4
    from psi4 import core

    if int(wfn.nirrep()) != 1:
        raise ValueError("psi4 active-space pack v1 requires single-irrep RHF reference")
    nmo = int(wfn.nmo())
    if n_active_orbitals > nmo:
        raise ValueError("active orbitals exceed nmo on Psi4 reference")
    if n_active_electrons % 2 != 0:
        raise ValueError("psi4 active-space pack v1 requires even electron count (RHF)")
    nfrozen = nmo - int(n_active_orbitals)
    nalpha = int(n_active_electrons) // 2
    nbeta = nalpha

    psi4.set_options(
        {
            "reference": "rhf",
            "frozen_uocc": nfrozen,
            "active": [int(n_active_orbitals)],
        }
    )
    _e, cas_wfn = psi4.energy("casci", ref_wfn=wfn, return_wfn=True)

    h_op = getattr(cas_wfn, "H", None)
    if h_op is not None and hasattr(h_op, "core_energy"):
        constant = float(h_op.core_energy())
        h1 = np.asarray(h_op.op(1), dtype=float)
        h2 = np.asarray(h_op.op(2), dtype=float)
        if h1.ndim == 2 and h2.ndim == 4:
            return constant, h1, h2

    return _active_space_from_mints_helper(wfn, n_active_orbitals, n_active_electrons)


def _active_space_from_mints_helper(
    wfn: Any,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Fallback: AO integrals + CASCI-style MO effective Hamiltonian."""
    from psi4 import core

    mints = core.MintsHelper(wfn)
    Ca = np.asarray(wfn.Ca(), dtype=float)
    nmo = int(Ca.shape[1])
    n_alpha = int(wfn.nalpha())
    n_beta = int(wfn.nbeta())
    if n_alpha != n_beta:
        raise ValueError("psi4 active-space pack v1 requires closed-shell RHF reference")
    n_active_pairs = int(n_active_electrons) // 2
    n_core_pairs = n_alpha - n_active_pairs
    if n_core_pairs < 0:
        raise ValueError("active electrons exceed total RHF electron count")
    active_start = int(n_core_pairs)
    if active_start + int(n_active_orbitals) > nmo:
        raise ValueError("active orbitals exceed available RHF orbital window")

    T = np.asarray(mints.T(), dtype=float)
    V = np.asarray(mints.V(), dtype=float)
    h_core_ao = T + V
    h_core_mo = np.asarray(Ca.T @ h_core_ao @ Ca, dtype=float)

    eri_ao = np.asarray(mints.ao_eri(), dtype=float)
    # Fallback path is rare and prioritizes correctness over minimal tensor work.
    eri_mo = np.asarray(
        np.einsum("pi,qj,rk,sl,pqrs->ijkl", Ca, Ca, Ca, Ca, eri_ao, optimize=True),
        dtype=float,
    )

    enuc = float(wfn.molecule().nuclear_repulsion_energy())
    return _casci_effective_blocks_from_mo_integrals(
        h_core_mo=h_core_mo,
        eri_mo_chemist=eri_mo,
        enuc=enuc,
        n_core_pairs=n_core_pairs,
        active_start=active_start,
        n_active_orbitals=int(n_active_orbitals),
    )

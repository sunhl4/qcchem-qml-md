from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.chem.pyscf_typing import (
    PyscfMeanField,
    as_complex_array,
    as_pyscf_cas,
    as_real_array,
    max_abs_imag,
)
from qchem_stack.quantum.algorithms.tolerances import (
    ACTIVE_SPACE_IMAG_TOLERANCE,
    ACTIVE_SPACE_IMAG_WARNING,
)


def _unwrap_mean_field_handle(rhf: Any) -> PyscfMeanField:
    """Return raw PySCF mean-field handle when wrapped by MeanFieldLike."""
    mf = rhf.mf
    if hasattr(mf, "raw_handle"):
        raw = mf.raw_handle()
        if raw is not mf:
            return raw
    return mf


def active_space_casci_raw_blocks(
    rhf: Any,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """CASCI MO integral blocks before OpenFermion reorder / dense restore.

    ``h2_spatial[p,q,r,s]`` is chemists' notation (pq|rs) over active spatial orbitals after dense restore.
    ``constant`` is PySCF CASCI ``energy_core`` from :meth:`pyscf.mcscf.CASCI.get_h1eff` (nuclear repulsion plus
    inactive-core contributions when ``ncore > 0``); it must not be summed again with ``energy_nuc``.

    ``h2eff`` from :meth:`pyscf.mcscf.CASCI.get_h2eff` may be **compact** (ndim ``!= 4``); callers should pass
    through :func:`pyscf.ao2mo.restore` before spatial reordering.
    """
    from pyscf import mcscf

    mf = _unwrap_mean_field_handle(rhf)
    meta = getattr(rhf, "driver_meta", None) or {}
    _ik = meta.get("pbc_active_space_kpoint_index")
    ik = int(_ik if _ik is not None else 0)
    mo_coeff = mf.mo_coeff
    if isinstance(mo_coeff, np.ndarray):
        mo = np.asarray(mo_coeff, dtype=float)
    else:
        moc = list(mo_coeff)
        if ik >= len(moc):
            ik = 0
        mo = as_complex_array(moc[ik])
        if max_abs_imag(mo, tol=ACTIVE_SPACE_IMAG_TOLERANCE) < ACTIVE_SPACE_IMAG_TOLERANCE:
            mo = as_real_array(mo)
    n_mo = int(mo.shape[1])
    if n_active_orbitals > n_mo:
        raise ValueError("active orbitals exceed MO count at chosen k-point")
    cas = as_pyscf_cas(mcscf.CASCI(mf, n_active_orbitals, n_active_electrons))
    frozen_cfg = list(meta.get("active_space_frozen_orbitals") or [])
    if frozen_cfg:
        if any(i < 0 for i in frozen_cfg):
            raise ValueError("active_space_frozen_orbitals entries must be >= 0.")
        if any(i >= n_mo for i in frozen_cfg):
            raise ValueError(
                f"active_space_frozen_orbitals index out of bounds for n_mo={n_mo}: {frozen_cfg}"
            )
        cas.frozen = sorted(set(int(i) for i in frozen_cfg))
    h1, e_core = cas.get_h1eff(mo)
    h2 = cas.get_h2eff(mo)
    h1a = np.asarray(h1, dtype=complex)
    h2a = np.asarray(h2, dtype=complex)
    for label, arr in (("h1", h1a), ("h2", h2a)):
        if max_abs_imag(arr) > ACTIVE_SPACE_IMAG_WARNING:
            raise ValueError(
                f"Active space {label} has non-trivial imaginary part; use Gamma (mesh [1,1,1]) or a real k-point."
            )
    # ``e_core`` from ``CASCI.get_h1eff`` / ``h1e_for_cas`` already starts at
    # ``energy_nuc()`` and adds inactive-orbital contributions when ``ncore > 0``;
    # do not add ``mol.energy_nuc()`` again (would double-count nuclear repulsion).
    constant = float(e_core)
    h1_out = as_real_array(h1a)
    h2_real = as_real_array(h2a)
    # PySCF 2.x ``get_h2eff`` often returns chemists' ERIs in compact 2D form
    # (``n * (n + 1) // 2`` square); OpenFermion expects full ``(n, n, n, n)``.
    n_act = int(n_active_orbitals)
    if h2_real.ndim == 4:
        h2_out = h2_real
    elif h2_real.ndim == 2:
        from pyscf import ao2mo

        h2_out = np.asarray(ao2mo.restore(1, h2_real, n_act), dtype=float)
    else:
        raise ValueError(f"unexpected active-space h2 shape {h2_real.shape} (ndim={h2_real.ndim})")
    return constant, h1_out, h2_out


def active_space_integrals(
    rhf: Any,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return (constant, h1_spatial, h2_spatial) for OpenFermion ``InteractionOperator``.

    ``h2_spatial`` is the active-space MO ERI tensor after OpenFermion reordering
    (:func:`~qchem_stack.chem.integral_convention.spatial_mo_eri_pyscf_to_openfermion_mo_ordering`)
    on PySCF ``get_h2eff`` / ``ao2mo.restore`` output. Callers then use
    ``spinorb_from_spatial`` and ``InteractionOperator(..., 0.5 * h2_spin_orb)``.

    The constant is PySCF ``get_h1eff``'s ``energy_core`` (nuclear repulsion plus
    frozen-core electronic energy when ``ncore>0``); do not add ``energy_nuc`` again.
    """
    from pyscf import ao2mo

    constant, h1_real, h2_store = active_space_casci_raw_blocks(
        rhf, n_active_orbitals, n_active_electrons
    )
    if h2_store.ndim != 4:
        h2a = np.asarray(
            ao2mo.restore(1, np.asarray(h2_store, dtype=float), int(n_active_orbitals)),
            dtype=float,
        )
    else:
        h2a = np.asarray(h2_store, dtype=float)
    from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering

    h2_spatial = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(h2a)
    return constant, h1_real, h2_spatial

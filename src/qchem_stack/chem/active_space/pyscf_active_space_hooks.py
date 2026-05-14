"""PySCF-specific active-space hooks behind :class:`~qchem_stack.chem.bridges.mean_field_reference.ClassicalMeanFieldReference`.

These may rotate ``mf.mo_coeff`` before CASCI-format active integrals are built. Other backends ignore
these hooks at the YAML layer (Psi4 placeholders raise ``supports_*=False`` gates).
"""

from __future__ import annotations

from typing import Any

import numpy as np

RESOLVED_ACTIVE_SPACE_META_KEY = "qchem_active_space_resolution_v1"


def _mo_energy_from_fock(mf: Any) -> np.ndarray:
    dm = mf.make_rdm1()
    fock = np.asarray(mf.get_fock(dm=dm), dtype=complex)
    mo = np.asarray(mf.mo_coeff, dtype=complex)
    orb = np.einsum("pi,pq,qj->ij", mo.conj(), fock, mo, optimize=True)
    return np.real(np.diagonal(orb)).astype(float)


def apply_pyscf_avas_to_reference(cfg: Any, reference: Any) -> None:
    """Run PySCF :class:`~pyscf.mcscf.avas.AVAS` then assign ``mf.mo_coeff``.

    Validates upstream tag / molecular branch / RHF. Writes
    :data:`RESOLVED_ACTIVE_SPACE_META_KEY` plus ``avas_atomic_projection_executed=True``.
    """
    if cfg.active_space.strategy != "avas":
        return

    tag = str((reference.driver_meta or {}).get("upstream_classical_software_tag", "")).lower()
    if tag != "pyscf":
        from qchem_stack.exceptions import PipelineError

        raise PipelineError(
            f"active_space.strategy='avas' requires upstream PySCF mean field (got upstream tag {tag!r})."
        )
    if cfg.chemistry_extended.pbc_cell_vectors_bohr is not None:
        from qchem_stack.exceptions import PipelineError

        raise PipelineError("AVAS is implemented on the molecular PySCF branch only (disable PBC).")
    if str(cfg.scf.method) != "RHF":
        from qchem_stack.exceptions import PipelineError

        raise PipelineError("AVAS currently requires restricted closed-shell scf.method='RHF'.")

    try:
        from pyscf.mcscf import avas as pyscf_avas
    except ImportError as exc:  # pragma: no cover
        from qchem_stack.exceptions import PipelineError

        raise PipelineError("PySCF mcscf.avas could not be imported.") from exc

    from qchem_stack.chem.drivers.pyscf_driver import (
        PySCFRHFResult,
        unwrap_pyscf_rhf_for_backend_operations,
    )

    pr: PySCFRHFResult = reference.as_pyscf_rhf_result()
    pr = unwrap_pyscf_rhf_for_backend_operations(pr)
    mf = pr.mf

    ce = cfg.chemistry_extended
    solver = pyscf_avas.AVAS(
        mf,
        list(ce.avas_ao_labels),
        threshold=float(ce.avas_threshold),
        minao=str(ce.avas_minao),
        with_iao=bool(ce.avas_with_iao),
        openshell_option=int(ce.avas_openshell_option),
        canonicalize=bool(ce.avas_canonicalize),
        ncore=int(ce.avas_ncore),
    )
    ncas, nelecas, mo_coeff = solver.kernel()
    mf.mo_coeff = mo_coeff
    reference.mo_energy = _mo_energy_from_fock(mf)  # type: ignore[attr-defined]
    reference.driver_meta[RESOLVED_ACTIVE_SPACE_META_KEY] = {
        "schema": RESOLVED_ACTIVE_SPACE_META_KEY,
        "source": "pyscf_mcscf_avas_kernel_v1",
        "n_active_orbitals": int(ncas),
        "n_active_electrons": int(nelecas),
        "threshold": float(ce.avas_threshold),
        "minao": str(ce.avas_minao),
        "with_iao": bool(ce.avas_with_iao),
        "openshell_option": int(ce.avas_openshell_option),
        "canonicalize": bool(ce.avas_canonicalize),
        "ncore": int(ce.avas_ncore),
    }
    reference.driver_meta["avas_atomic_projection_executed"] = True


def patch_experiment_active_space_resolution(cfg: Any, reference: Any) -> Any:
    """Synchronize YAML active-space sizing with AVAS-derived ``ncas`` / ``nelecas``."""
    meta = reference.driver_meta or {}
    res = meta.get(RESOLVED_ACTIVE_SPACE_META_KEY)
    if not isinstance(res, dict):
        return cfg
    n_a = res.get("n_active_orbitals")
    n_e = res.get("n_active_electrons")
    if n_a is None or n_e is None:
        return cfg
    n_act, n_el = int(n_a), int(n_e)
    a = cfg.active_space
    if int(a.n_active_orbitals) == n_act and int(a.n_active_electrons) == n_el:
        return cfg
    new_as = a.model_copy(
        update={
            "ncas": n_act,
            "nelecas": n_el,
            "n_active_orbitals": n_act,
            "n_active_electrons": n_el,
        }
    )
    return cfg.model_copy(update={"active_space": new_as})


def casscf_energy_and_maybe_orbitals(
    cfg: Any,
    reference: Any,
    *,
    update_integrals_orbitals: bool,
    record_audit: bool,
) -> None:
    """One ``pyscf.mcscf.CASSCF`` optimization pass for auditing and/or integral-path orbitals."""
    if not update_integrals_orbitals and not record_audit:
        return

    tag = str((reference.driver_meta or {}).get("upstream_classical_software_tag", "")).lower()
    if tag != "pyscf":
        from qchem_stack.exceptions import PipelineError

        raise PipelineError(f"CASSCF orbital hooks require PySCF upstream (got tag {tag!r}).")
    if cfg.chemistry_extended.pbc_cell_vectors_bohr is not None:
        from qchem_stack.exceptions import PipelineError

        raise PipelineError("CASSCF hooks are unsupported on the PBC branch.")

    try:
        from pyscf import mcscf
    except ImportError as exc:  # pragma: no cover
        from qchem_stack.exceptions import PipelineError

        raise PipelineError("PySCF mcscf is required for CASSCF hooks.") from exc

    from qchem_stack.chem.drivers.pyscf_driver import (
        PySCFRHFResult,
        unwrap_pyscf_rhf_for_backend_operations,
    )

    pr: PySCFRHFResult = reference.as_pyscf_rhf_result()
    pr = unwrap_pyscf_rhf_for_backend_operations(pr)
    mf = pr.mf

    meta_resolution = reference.driver_meta.get(RESOLVED_ACTIVE_SPACE_META_KEY)
    if isinstance(meta_resolution, dict):
        ncas = int(meta_resolution["n_active_orbitals"])
        nelec = int(meta_resolution["n_active_electrons"])
    else:
        ncas = int(cfg.active_space.n_active_orbitals)
        nelec = int(cfg.active_space.n_active_electrons)

    mc = mcscf.CASSCF(mf, ncas, nelec)
    ret = mc.kernel()
    e_casscf = float(ret[0] if isinstance(ret, tuple) else ret)

    merged_audit = {
        "schema": "casscf_orbital_audit_v1",
        "active_spatial_orbitals": ncas,
        "active_electrons": nelec,
        "casscf_energy_au": e_casscf,
        "mo_coeff_rotated_into_casscf": bool(update_integrals_orbitals),
        "note": (
            "PySCF mcscf.CASSCF on the current molecular reference orbitals "
            "(``chemistry_extended.casscf_orbital_optimization_audit`` records energy; "
            "``casscf_orbital_optimization_for_integrals`` additionally rotates ``mf.mo_coeff`` into "
            "an optimized CAS orbital basis before CASCI-style active extracts)."
        ),
    }

    if update_integrals_orbitals:
        mf.mo_coeff = mc.mo_coeff
        reference.mo_energy = _mo_energy_from_fock(mf)  # type: ignore[attr-defined]

    if record_audit:
        reference.driver_meta["casscf_orbital_audit_v1"] = merged_audit

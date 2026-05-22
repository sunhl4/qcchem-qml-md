"""PySCF-specific active-space hooks (CASSCF audit / integral-path orbital rotation).

AVAS threshold projection lives in :mod:`qchem_stack.chem.active_space.avas_projection` (PySCF kernel;
Psi4 imports MO via shadow reference). These hooks may rotate ``mf.mo_coeff`` before CASCI-format
active integrals are built on PySCF upstream references.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.chem.active_space.resolution import (
    RESOLVED_ACTIVE_SPACE_META_KEY,
    patch_experiment_active_space_resolution,
)
from qchem_stack.contracts.schema_ids import CASSCF_ORBITAL_AUDIT_V1

__all__ = [
    "RESOLVED_ACTIVE_SPACE_META_KEY",
    "casscf_energy_and_maybe_orbitals",
    "patch_experiment_active_space_resolution",
]


def _mo_energy_from_fock(mf: Any) -> np.ndarray:
    dm = mf.make_rdm1()
    fock = np.asarray(mf.get_fock(dm=dm), dtype=complex)
    mo = np.asarray(mf.mo_coeff, dtype=complex)
    orb = np.einsum("pi,pq,qj->ij", mo.conj(), fock, mo, optimize=True)
    return np.real(np.diagonal(orb)).astype(float)


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
    if cfg.chemistry_extended.pbc.cell_vectors_bohr is not None:
        from qchem_stack.exceptions import PipelineError

        raise PipelineError("CASSCF hooks are unsupported on the PBC branch.")

    try:
        from pyscf import mcscf
    except ImportError as exc:  # pragma: no cover
        from qchem_stack.exceptions import PipelineError

        raise PipelineError("PySCF mcscf is required for CASSCF hooks.") from exc

    from qchem_stack.chem.drivers.pyscf_driver_types import (
        PySCFRHFResult,
        unwrap_pyscf_rhf_for_backend_operations,
    )
    from qchem_stack.chem.pyscf_typing import as_pyscf_cas, as_pyscf_mf

    pr: PySCFRHFResult = reference.as_pyscf_rhf_result()
    pr = unwrap_pyscf_rhf_for_backend_operations(pr)
    mf_p = as_pyscf_mf(pr.mf)

    meta_resolution = reference.driver_meta.get(RESOLVED_ACTIVE_SPACE_META_KEY)
    if isinstance(meta_resolution, dict):
        ncas = int(meta_resolution["n_active_orbitals"])
        nelec = int(meta_resolution["n_active_electrons"])
    else:
        ncas = int(cfg.active_space.cas.n_orbitals)
        nelec = int(cfg.active_space.cas.n_electrons)

    mc = as_pyscf_cas(mcscf.CASSCF(mf_p, ncas, nelec))
    ret = mc.kernel()
    e_casscf = float(ret[0] if isinstance(ret, tuple) else ret)

    merged_audit = {
        "schema": CASSCF_ORBITAL_AUDIT_V1,
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
        mf_p.mo_coeff = mc.mo_coeff
        reference.mo_energy = _mo_energy_from_fock(mf_p)  # type: ignore[attr-defined]

    if record_audit:
        reference.driver_meta["casscf_orbital_audit_v1"] = merged_audit

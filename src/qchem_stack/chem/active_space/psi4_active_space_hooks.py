"""Psi4 active-space hooks (AVAS via shared projection; CASSCF via Psi4 API)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.active_space.avas_projection import apply_avas_projection
from qchem_stack.chem.active_space.pyscf_active_space_hooks import (
    RESOLVED_ACTIVE_SPACE_META_KEY,
)
from qchem_stack.chem.bridges.ao_basis_view import ao_basis_view_from_reference
from qchem_stack.contracts.schema_ids import CASSCF_ORBITAL_AUDIT_V1
from qchem_stack.exceptions import PipelineError

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def _unwrap_wfn(reference: ClassicalMeanFieldReference) -> Any:
    mf = reference.mf
    if hasattr(mf, "raw_handle"):
        return mf.raw_handle()
    return mf


class Psi4ActiveSpaceHooks:
    def apply_avas(self, cfg: ExperimentConfig, reference: ClassicalMeanFieldReference) -> None:
        apply_avas_projection(cfg, reference)

    def casscf_energy_and_maybe_orbitals(
        self,
        cfg: ExperimentConfig,
        reference: ClassicalMeanFieldReference,
        *,
        update_integrals_orbitals: bool,
        record_audit: bool,
    ) -> None:
        if not update_integrals_orbitals and not record_audit:
            return
        if cfg.chemistry_extended.pbc.cell_vectors_bohr is not None:
            raise PipelineError("CASSCF orbital hooks are unsupported on the PBC branch.")
        if str(cfg.scf.method) != "RHF":
            raise PipelineError("casscf_orbital_* hooks require scf.method=RHF.")

        import psi4

        wfn = _unwrap_wfn(reference)
        meta_resolution = reference.driver_meta.get(RESOLVED_ACTIVE_SPACE_META_KEY)
        if isinstance(meta_resolution, dict):
            ncas = int(meta_resolution["n_active_orbitals"])
            nelec = int(meta_resolution["n_active_electrons"])
        else:
            ncas = int(cfg.active_space.cas.n_orbitals)
            nelec = int(cfg.active_space.cas.n_electrons)

        nmo = int(wfn.nmo())
        nfrozen = nmo - ncas
        nelec // 2
        psi4.set_options(
            {
                "reference": "rhf",
                "frozen_uocc": int(nfrozen),
                "active": [int(ncas)],
            }
        )
        e_casscf, cas_wfn = psi4.energy("casscf", ref_wfn=wfn, return_wfn=True)
        e_casscf = float(e_casscf)

        merged_audit = {
            "schema": CASSCF_ORBITAL_AUDIT_V1,
            "active_spatial_orbitals": ncas,
            "active_electrons": nelec,
            "casscf_energy_au": e_casscf,
            "mo_coeff_rotated_into_casscf": bool(update_integrals_orbitals),
            "note": (
                "Psi4 casscf on the current RHF reference; "
                "``casscf_orbital_optimization_for_integrals`` rotates Ca when supported."
            ),
        }

        if update_integrals_orbitals:
            ca_new = np.asarray(cas_wfn.Ca(), dtype=float)
            wfn.Ca().copy(ca_new)
            ao = ao_basis_view_from_reference(reference)
            reference.mo_energy = np.real(  # type: ignore[attr-defined]
                np.diagonal(ca_new.T @ ao.fock_ao() @ ca_new)
            ).astype(float)

        if record_audit:
            reference.driver_meta["casscf_orbital_audit_v1"] = merged_audit

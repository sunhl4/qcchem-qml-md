"""AVAS orbital projection (PySCF ``mcscf.avas`` kernel; Psi4 via shadow PySCF reference)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.chem.active_space.pyscf_active_space_hooks import _mo_energy_from_fock
from qchem_stack.chem.active_space.resolution import RESOLVED_ACTIVE_SPACE_META_KEY
from qchem_stack.chem.bridges.ao_basis_view import (
    PySCFAOBasisView,
    ao_basis_view_from_reference,
)
from qchem_stack.chem.bridges.pyscf_shadow_reference import build_pyscf_rhf_shadow
from qchem_stack.chem.integration.meta_schema import (
    append_kernel_bindings,
    binding_avas_projection,
)
from qchem_stack.exceptions import PipelineError

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def apply_avas_projection(cfg: ExperimentConfig, reference: ClassicalMeanFieldReference) -> None:
    """Run AVAS and update reference MO coefficients + driver_meta."""
    if cfg.active_space.strategy != "avas":
        return
    if cfg.chemistry_extended.pbc.cell_vectors_bohr is not None:
        raise PipelineError("AVAS is implemented on the molecular branch only (disable PBC).")
    if str(cfg.scf.method) != "RHF":
        raise PipelineError("AVAS currently requires restricted closed-shell scf.method='RHF'.")

    try:
        from pyscf.mcscf import avas as pyscf_avas
    except ImportError as exc:  # pragma: no cover
        raise PipelineError("PySCF mcscf.avas could not be imported.") from exc

    ao = ao_basis_view_from_reference(reference)
    if isinstance(ao, PySCFAOBasisView):
        mf = ao.raw_handle()
        avas_source = "pyscf_mcscf_avas_kernel_v1"
    else:
        mf = build_pyscf_rhf_shadow(cfg, reference, run_scf_if_needed=False)
        avas_source = "pyscf_mcscf_avas_on_imported_mo_v1"

    ce = cfg.chemistry_extended
    solver = pyscf_avas.AVAS(
        mf,
        list(ce.avas.ao_labels),
        threshold=float(ce.avas.threshold),
        minao=str(ce.avas.minao),
        with_iao=bool(ce.avas.with_iao),
        openshell_option=int(ce.avas.openshell_option),
        canonicalize=bool(ce.avas.canonicalize),
        ncore=int(ce.avas.ncore),
    )
    ncas, nelecas, mo_coeff = solver.kernel()
    mo_out = np.asarray(mo_coeff, dtype=float)

    tag = reference.backend_tag()
    if tag == "pyscf":
        from qchem_stack.chem.pyscf_typing import as_pyscf_mf

        as_pyscf_mf(reference.mf).mo_coeff = mo_out
        mf_ref = as_pyscf_mf(reference.mf)
        reference.mo_energy = _mo_energy_from_fock(mf_ref)  # type: ignore[attr-defined]
    elif tag == "psi4":
        from qchem_stack.chem.integrals.psi4_reference_api import psi4_set_ca

        wfn = reference.mf.raw_handle() if hasattr(reference.mf, "raw_handle") else reference.mf
        psi4_set_ca(wfn, mo_out)
        eps = np.real(np.diagonal(mo_out.T @ ao.fock_ao() @ mo_out)).astype(float)
        reference.mo_energy = eps  # type: ignore[attr-defined]
    else:
        raise PipelineError(f"AVAS MO write-back unsupported for backend {tag!r}.")

    reference.driver_meta[RESOLVED_ACTIVE_SPACE_META_KEY] = {
        "schema": RESOLVED_ACTIVE_SPACE_META_KEY,
        "source": avas_source,
        "n_active_orbitals": int(ncas),
        "n_active_electrons": int(nelecas),
        "threshold": float(ce.avas.threshold),
        "minao": str(ce.avas.minao),
        "with_iao": bool(ce.avas.with_iao),
        "openshell_option": int(ce.avas.openshell_option),
        "canonicalize": bool(ce.avas.canonicalize),
        "ncore": int(ce.avas.ncore),
    }
    reference.driver_meta["avas_atomic_projection_executed"] = True
    append_kernel_bindings(
        reference.driver_meta,
        [
            binding_avas_projection(
                "pyscf",
                str(avas_source),
                native=(tag == "pyscf"),
            )
        ],
    )

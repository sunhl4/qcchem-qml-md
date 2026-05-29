"""Mean-field execution (molecular and PBC) for :class:`PySCFIntegralSolver`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.mean_field_like import wrap_mean_field_like
from qchem_stack.chem.pyscf_typing import as_pyscf_cas
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult
from qchem_stack.chem.solvers.pyscf_solver_common import require_pyscf
from qchem_stack.chem.solvers.pyscf_solver_setup import (
    apply_scf_controls,
    augment_meta_with_ddcosmo,
    base_driver_meta,
    build_mean_field_factory,
    chkfile_present,
    make_pbc_cell,
)

if TYPE_CHECKING:
    from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver


def build_molecular_mf_without_kernel(solver: PySCFIntegralSolver) -> Any:
    gto, scf = require_pyscf()
    mf = build_mean_field_factory(solver, gto, scf)
    apply_scf_controls(solver, mf, chkfile_present=chkfile_present(solver))
    return mf


def idle_molecular_driver_meta(solver: PySCFIntegralSolver) -> dict[str, Any]:
    meta = base_driver_meta(
        solver,
        pbc=False,
        pbc_kpoint_mesh=None,
        pbc_active_space_kpoint_index=None,
    )
    return augment_meta_with_ddcosmo(solver, meta)


def execute_molecular_mean_field(solver: PySCFIntegralSolver) -> MolecularMeanFieldResult:
    if solver.chemistry_extended.pbc.cell_vectors_bohr is not None:
        raise ValueError(
            "molecular branch requires a non-PBC config; use compute_mean_field(periodic=True)."
        )
    gto, scf = require_pyscf()
    mf = build_mean_field_factory(solver, gto, scf)
    apply_scf_controls(solver, mf, chkfile_present=chkfile_present(solver))
    meta = base_driver_meta(
        solver,
        pbc=False,
        pbc_kpoint_mesh=None,
        pbc_active_space_kpoint_index=None,
    )
    meta = augment_meta_with_ddcosmo(solver, meta)
    mf_p = as_pyscf_cas(mf)
    e = float(mf_p.kernel())
    mo_e = np.asarray(mf_p.mo_energy, dtype=float)
    return MolecularMeanFieldResult(
        mf=wrap_mean_field_like(backend_tag="pyscf", raw_mf=mf_p, e_tot=e, mo_energy=mo_e),
        e_tot=e,
        mo_energy=mo_e,
        driver_meta=meta,
    )


def execute_periodic_mean_field(solver: PySCFIntegralSolver) -> MolecularMeanFieldResult:
    pbc = solver.chemistry_extended.pbc.cell_vectors_bohr
    if pbc is None:
        raise ValueError("periodic branch requires chemistry_extended.pbc.cell_vectors_bohr")
    if solver.method != "RHF":
        raise ValueError("PBC branch requires scf.method=RHF (KRHF/k-mesh).")
    try:
        from pyscf.pbc import gto as pbc_gto
        from pyscf.pbc import scf as pbc_scf
    except ImportError as e:  # pragma: no cover
        raise ImportError("PySCF with pbc is required.") from e
    cell = make_pbc_cell(solver, pbc_gto)
    cell.build()
    mesh = list(solver.chemistry_extended.pbc.kpoint_mesh)
    if any(m < 1 for m in mesh):
        raise ValueError("pbc_kpoint_mesh entries must be >= 1")
    use_k = max(mesh) > 1
    if use_k:
        kpts = cell.make_kpts(mesh)
        mf = pbc_scf.khf.KRHF(cell, kpts)
        kpa = np.asarray(kpts)
        n_k = int(kpa.shape[0])
    else:
        mf = pbc_scf.hf.RHF(cell)
        n_k = 1

    apply_scf_controls(solver, mf, chkfile_present=chkfile_present(solver))

    meta = base_driver_meta(
        solver,
        pbc=True,
        pbc_kpoint_mesh=mesh,
        pbc_active_space_kpoint_index=int(solver.chemistry_extended.pbc.active_space_kpoint_index),
    )
    meta.update(
        {
            "gamma_only": not use_k,
            "n_kpoints": n_k,
            "cell_vectors_bohr": [list(map(float, row)) for row in pbc],
        }
    )
    if solver.chemistry_extended.pbc.active_space_kpoint_index >= n_k:
        raise ValueError(
            f"pbc_active_space_kpoint_index={solver.chemistry_extended.pbc.active_space_kpoint_index} "
            f"out of range for n_kpoints={n_k}"
        )
    if solver.chemistry_extended.solvent.model == "ddcosmo":
        from pyscf import solvent

        try:
            mf = as_pyscf_cas(solvent.ddCOSMO(mf))
            mf.with_solvent.eps = float(solver.chemistry_extended.solvent.epsilon)
            meta["solvent"] = "ddcosmo"
            meta["ddcosmo_epsilon"] = float(solver.chemistry_extended.solvent.epsilon)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError("ddCOSMO on this periodic mean-field object failed.") from exc
    mf_p = as_pyscf_cas(mf)
    e_tot = float(mf_p.kernel())
    mo_ev = mf_p.mo_energy
    if isinstance(mo_ev, (list, tuple)):
        ik = int(solver.chemistry_extended.pbc.active_space_kpoint_index)
        mo_e_out = np.asarray(mo_ev[ik], dtype=float)
    else:
        mo_e_out = np.asarray(mo_ev, dtype=float)
    return MolecularMeanFieldResult(
        mf=wrap_mean_field_like(backend_tag="pyscf", raw_mf=mf_p, e_tot=e_tot, mo_energy=mo_e_out),
        e_tot=e_tot,
        mo_energy=mo_e_out,
        driver_meta=meta,
    )

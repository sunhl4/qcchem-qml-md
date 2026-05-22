"""Molecule construction, SCF controls, and driver metadata for PySCF."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, cast

import numpy as np

from qchem_stack.chem.integration.meta_schema import (
    binding_mean_field_scf,
    merge_integration_driver_meta,
)
from qchem_stack.chem.solvers.pyscf_solver_common import pyscf_version_or_unknown

if TYPE_CHECKING:
    from qchem_stack.chem.pyscf_typing import PyscfMeanField
    from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver


def scf_control_meta(solver: PySCFIntegralSolver) -> dict[str, Any]:
    return {
        "scf_chkfile": solver.chkfile,
        "scf_init_guess": solver.init_guess,
        "scf_level_shift": float(solver.level_shift) if solver.level_shift is not None else None,
        "scf_use_newton": bool(solver.use_newton),
        "scf_diis_space_dimension": (
            int(solver.diis_space_dimension) if solver.diis_space_dimension is not None else None
        ),
        "scf_density_fit": bool(solver.density_fit),
        "scf_density_fit_auxbasis": str(solver.density_fit_auxbasis)
        if solver.density_fit_auxbasis
        else None,
    }


def atom_block(solver: PySCFIntegralSolver) -> str:
    parts = []
    for sym, xyz in zip(solver.system.symbols, solver.system.coordinates_bohr, strict=True):
        parts.append(f"{sym} {float(xyz[0]):.12f} {float(xyz[1]):.12f} {float(xyz[2]):.12f}")
    return "; ".join(parts)


def make_mol(solver: PySCFIntegralSolver, gto: Any) -> Any:
    symm_kw: dict[str, Any] = {}
    symm = solver.chemistry_extended.symmetry.pyscf_symmetry
    if symm is not False and symm is not None:
        if isinstance(symm, str):
            if not str(symm).strip():
                raise ValueError("chemistry_extended.pyscf_symmetry string must be non-empty.")
            symm_kw["symmetry"] = str(symm)
        else:
            symm_kw["symmetry"] = bool(symm)
    return gto.M(
        atom=atom_block(solver),
        basis=solver.system.basis,
        ecp=solver.system.ecp,
        charge=solver.system.charge,
        spin=solver.system.multiplicity - 1,
        unit="Bohr",
        **symm_kw,
    )


def base_driver_meta(
    solver: PySCFIntegralSolver,
    *,
    pbc: bool,
    pbc_kpoint_mesh: list[int] | None,
    pbc_active_space_kpoint_index: int | None,
) -> dict[str, Any]:
    solv = solver.chemistry_extended.solvent.model
    meta: dict[str, Any] = {
        "driver_meta_schema_version": 1,
        "driver_family": "pyscf",
        "scf_method": solver.method,
        "integral_representation": "mo",
        "solvent_model": str(solv),
        "ddcosmo_epsilon": float(solver.chemistry_extended.solvent.epsilon)
        if solv == "ddcosmo"
        else None,
        "pbc": bool(pbc),
        "pbc_kpoint_mesh": list(pbc_kpoint_mesh) if pbc_kpoint_mesh is not None else None,
        "pbc_active_space_kpoint_index": (
            int(pbc_active_space_kpoint_index)
            if pbc_active_space_kpoint_index is not None
            else None
        ),
        "energy_accounting_model": "mf_e_tot_direct",
        "pyscf_version": pyscf_version_or_unknown(),
        "pyscf_symmetry": solver.chemistry_extended.symmetry.pyscf_symmetry,
        "ecp": solver.system.ecp,
    }
    meta.update(scf_control_meta(solver))
    return merge_integration_driver_meta(
        meta,
        backend_tag="pyscf",
        driver_family="pyscf",
        kernel_bindings=[
            binding_mean_field_scf("pyscf", "pyscf_native_v1", native=True),
        ],
    )


def apply_scf_controls(solver: PySCFIntegralSolver, mf: Any, *, chkfile_present: bool) -> None:
    if solver.chkfile:
        mf.chkfile = solver.chkfile
    if solver.scf_max_cycle is not None:
        mf.max_cycle = int(solver.scf_max_cycle)
    if solver.init_guess is not None:
        mf.init_guess = solver.init_guess
    elif solver.chkfile:
        mf.init_guess = "chkfile" if chkfile_present else "minao"
    if solver.level_shift is not None and hasattr(mf, "level_shift"):
        mf.level_shift(float(solver.level_shift))
    if solver.diis_space_dimension is not None and hasattr(mf, "diis_space"):
        mf.diis_space = int(solver.diis_space_dimension)


def chkfile_present(solver: PySCFIntegralSolver) -> bool:
    return bool(solver.chkfile and Path(solver.chkfile).is_file())


def augment_meta_with_ddcosmo(solver: PySCFIntegralSolver, meta: dict[str, Any]) -> dict[str, Any]:
    if solver.chemistry_extended.solvent.model == "ddcosmo":
        meta["solvent"] = "ddcosmo"
        meta["ddcosmo_epsilon"] = float(solver.chemistry_extended.solvent.epsilon)
    return meta


def build_mean_field_factory(
    solver: PySCFIntegralSolver, gto_mod: Any, scf_mod: Any
) -> PyscfMeanField:
    mol = make_mol(solver, gto_mod)
    method = cast("Literal['RHF', 'ROHF', 'UHF']", solver.method)
    if method == "RHF":
        mf: PyscfMeanField = cast("PyscfMeanField", scf_mod.RHF(mol))
    elif method == "ROHF":
        mf = cast("PyscfMeanField", scf_mod.ROHF(mol))
    else:
        mf = cast("PyscfMeanField", scf_mod.UHF(mol))
    if solver.use_newton and method in ("RHF", "ROHF") and hasattr(mf, "newton"):
        mf = cast("PyscfMeanField", mf.newton())
    if solver.chemistry_extended.solvent.model == "ddcosmo":
        from pyscf import solvent

        mf = cast("PyscfMeanField", solvent.ddCOSMO(mf))
        mf.with_solvent.eps = float(solver.chemistry_extended.solvent.epsilon)
    if solver.density_fit and hasattr(mf, "density_fit"):
        if solver.density_fit_auxbasis:
            mf = cast("PyscfMeanField", mf.density_fit(auxbasis=solver.density_fit_auxbasis))
        else:
            mf = cast("PyscfMeanField", mf.density_fit())
    return mf


def make_pbc_cell(solver: PySCFIntegralSolver, gto_pbc: Any) -> Any:
    pbc = solver.chemistry_extended.pbc.cell_vectors_bohr
    assert pbc is not None
    a = np.asarray(pbc, dtype=float)
    return gto_pbc.M(
        atom=atom_block(solver),
        a=a,
        basis=solver.system.basis,
        charge=solver.system.charge,
        spin=solver.system.multiplicity - 1,
        unit="Bohr",
    )

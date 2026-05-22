"""Mean-field execution (molecular and PBC) for :class:`Psi4IntegralSolver`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.integrals.psi4_reference_api import psi4_nao, psi4_nmo
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult
from qchem_stack.chem.solvers.psi4_solver_setup import (
    base_driver_meta,
    normalize_coords_bohr,
    psi4_geometry_block,
    psi4_scf_options,
    validate_symbols_coords,
)
from qchem_stack.config import ChemistryExtendedSpec
from qchem_stack.config.scf_helpers import resolve_scf_max_cycle

if TYPE_CHECKING:
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver


def scf_energy_with_wavefunction(
    *,
    symbols: list[str],
    coords_bohr: np.ndarray,
    charge: int,
    multiplicity: int,
    basis: str,
    method: str,
    max_cycle: int | None,
    chemistry_extended: ChemistryExtendedSpec | None = None,
    cell_vectors_bohr: np.ndarray | None = None,
) -> tuple[float | None, np.ndarray | None, Any | None, str | None]:
    try:
        geom = normalize_coords_bohr(coords_bohr)
        validate_symbols_coords(symbols, geom)
    except ValueError as exc:
        return None, None, None, str(exc)

    try:
        import psi4
    except ImportError:
        return None, None, None, "psi4_import_missing"

    ce = chemistry_extended or ChemistryExtendedSpec()
    try:
        psi4.core.clean()
        psi4.core.clean_options()
        geom_block = psi4_geometry_block(
            charge=int(charge),
            multiplicity=int(multiplicity),
            symbols=list(symbols),
            coords_bohr=geom,
        )
        mol = psi4.geometry(geom_block)
        if cell_vectors_bohr is not None:
            a = np.asarray(cell_vectors_bohr, dtype=float)
            mol.set_lattice_vectors(a[0].tolist(), a[1].tolist(), a[2].tolist())
        psi4.set_options(
            psi4_scf_options(
                basis=basis,
                method=method,
                max_cycle=max_cycle,
                chemistry_extended=ce,
            )
        )
        e_au, wfn = psi4.energy("scf", molecule=mol, return_wfn=True)
        mo = np.asarray(wfn.Ca(), dtype=float)
        try:
            eps_a = wfn.epsilon_a()
            if hasattr(eps_a, "np"):
                mo_e = np.asarray(eps_a.np, dtype=float)
            else:
                mo_e = np.real(np.diagonal(mo.T @ np.asarray(wfn.H().np, dtype=float) @ mo)).astype(
                    float
                )
        except Exception:
            mo_e = np.real(np.diagonal(mo.T @ np.asarray(wfn.H().np, dtype=float) @ mo)).astype(
                float
            )
        return float(e_au), mo_e, wfn, None
    except Exception as exc:  # noqa: BLE001
        return None, None, None, f"{type(exc).__name__}: {exc}"


def psi4_hf_total_energy_au(
    *,
    symbols: list[str],
    coords_bohr: np.ndarray,
    charge: int,
    multiplicity: int,
    basis: str,
) -> tuple[float | None, str | None]:
    e_au, _, _, reason = scf_energy_with_wavefunction(
        symbols=list(symbols),
        coords_bohr=np.asarray(coords_bohr, dtype=float),
        charge=int(charge),
        multiplicity=int(multiplicity),
        basis=str(basis),
        method="RHF",
        max_cycle=None,
    )
    return e_au, reason


def execute_molecular_mean_field(solver: Psi4IntegralSolver) -> MolecularMeanFieldResult:
    if solver.chemistry_extended.pbc.cell_vectors_bohr is not None:
        raise ValueError(
            "molecular branch requires non-PBC config; use compute_mean_field(periodic=True)."
        )
    e_au, mo_energies, wfn, reason = scf_energy_with_wavefunction(
        symbols=list(solver._system.symbols),
        coords_bohr=np.asarray(solver._system.coordinates_bohr, dtype=float),
        charge=int(solver._system.charge),
        multiplicity=int(solver._system.multiplicity),
        basis=str(solver._system.basis),
        method=str(solver._method),
        max_cycle=resolve_scf_max_cycle(solver._cfg.scf),
        chemistry_extended=solver.chemistry_extended,
    )
    if e_au is None or wfn is None:
        raise RuntimeError(f"Psi4 SCF unavailable: {reason}")
    if mo_energies is None:
        mo_energies = np.asarray([float(e_au)], dtype=float)
    nmo = psi4_nmo(wfn)
    result = MolecularMeanFieldResult(
        mf=wfn,
        e_tot=float(e_au),
        mo_energy=np.asarray(mo_energies, dtype=float),
        driver_meta=base_driver_meta(
            solver,
            reason=None,
            extra={
                "nmo": nmo,
                "nao": psi4_nao(wfn),
                "mo_coeff_shape": list(np.asarray(wfn.Ca()).shape),
                "psi4_reference_class": type(wfn).__name__,
            },
        ),
    )
    solver._last_molecular_mf_result = result
    return result


def execute_periodic_mean_field(solver: Psi4IntegralSolver) -> MolecularMeanFieldResult:
    pbc = solver.chemistry_extended.pbc.cell_vectors_bohr
    if pbc is None:
        raise ValueError("periodic branch requires chemistry_extended.pbc.cell_vectors_bohr")
    if solver._method != "RHF":
        raise ValueError("Psi4 PBC branch requires scf.method=RHF.")
    mesh = list(solver.chemistry_extended.pbc.kpoint_mesh)
    if any(m < 1 for m in mesh):
        raise ValueError("pbc_kpoint_mesh entries must be >= 1")
    if max(mesh) > 1:
        raise NotImplementedError(
            "Psi4 adapter PBC currently supports Gamma-only (pbc_kpoint_mesh all 1)."
        )
    e_au, mo_energies, wfn, reason = scf_energy_with_wavefunction(
        symbols=list(solver._system.symbols),
        coords_bohr=np.asarray(solver._system.coordinates_bohr, dtype=float),
        charge=int(solver._system.charge),
        multiplicity=int(solver._system.multiplicity),
        basis=str(solver._system.basis),
        method="RHF",
        max_cycle=resolve_scf_max_cycle(solver._cfg.scf),
        chemistry_extended=solver.chemistry_extended,
        cell_vectors_bohr=np.asarray(pbc, dtype=float),
    )
    if e_au is None or wfn is None:
        raise RuntimeError(f"Psi4 periodic SCF unavailable: {reason}")
    result = MolecularMeanFieldResult(
        mf=wfn,
        e_tot=float(e_au),
        mo_energy=np.asarray(mo_energies, dtype=float),
        driver_meta=base_driver_meta(
            solver,
            reason=None,
            extra={
                "pbc": True,
                "pbc_kpoint_mesh": mesh,
                "cell_vectors_bohr": [list(map(float, row)) for row in pbc],
                "gamma_only": True,
            },
        ),
    )
    solver._last_molecular_mf_result = result
    return result

"""Tiny closed-shell HF cross-checks between PySCF and optional Psi4 (W10 baseline)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np

from qchem_stack.chem.solvers.psi4_solver import psi4_hf_total_energy_au
from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ChemistryExtendedSpec


def _closed_shell_cases() -> list[tuple[str, int, int, list[str], list[list[float]], str]]:
    return [
        ("h2_r1p4_bohr_sto3g", 0, 1, ["H", "H"], [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]], "sto-3g"),
        ("h2_r2p0_bohr_sto3g", 0, 1, ["H", "H"], [[0.0, 0.0, 0.0], [0.0, 0.0, 2.0]], "sto-3g"),
        ("he_sto3g", 0, 1, ["He"], [[0.0, 0.0, 0.0]], "sto-3g"),
    ]


def pyscf_rhf_total_energy_au(
    *,
    symbols: list[str],
    coords_bohr: Iterable[list[float]] | np.ndarray,
    charge: int,
    multiplicity: int,
    basis: str,
) -> float:
    arr = np.asarray(list(coords_bohr), dtype=float)
    sys = MolecularSystem(
        symbols=list(symbols),
        coordinates_bohr=arr,
        charge=int(charge),
        multiplicity=int(multiplicity),
        basis=str(basis),
    )
    sol = PySCFIntegralSolver(sys, "RHF", ChemistryExtendedSpec())
    return float(sol.compute_mean_field(periodic=False).e_tot)


def build_cross_solver_parity_report(*, atol: float = 5e-4) -> dict[str, Any]:
    """HF total energies from PySCF; Psi4 deltas when ``import psi4`` succeeds."""
    cases_out: list[dict[str, Any]] = []
    psi4_any = False
    for name, chg, mult, syms, xyz, basis in _closed_shell_cases():
        xyz_a = np.asarray(xyz, dtype=float)
        e_pyscf = pyscf_rhf_total_energy_au(
            symbols=syms, coords_bohr=xyz_a, charge=chg, multiplicity=mult, basis=basis
        )
        e_psi4, psi4_reason = psi4_hf_total_energy_au(
            symbols=syms, coords_bohr=xyz_a, charge=chg, multiplicity=mult, basis=basis
        )
        if e_psi4 is not None:
            psi4_any = True
        delta = abs(float(e_pyscf) - float(e_psi4)) if e_psi4 is not None else None
        tol_ok = delta is not None and float(delta) <= float(atol)
        cases_out.append(
            {
                "case_id": name,
                "basis": basis,
                "charge": chg,
                "multiplicity": mult,
                "pyscf_hf_total_au": e_pyscf,
                "psi4_hf_total_au": e_psi4,
                "psi4_skip_reason": psi4_reason,
                "abs_delta_au": delta,
                "within_atol": tol_ok if delta is not None else None,
            }
        )

    summary = {"psi4_installed": psi4_any, "n_cases": len(cases_out), "atol": float(atol)}
    if psi4_any:
        flags = [c["within_atol"] for c in cases_out if c["abs_delta_au"] is not None]
        summary["all_within_atol"] = bool(flags) and all(flags)
    else:
        summary["all_within_atol"] = None

    return {"schema": "cross_solver_hf_parity_v1", "summary": summary, "cases": cases_out}

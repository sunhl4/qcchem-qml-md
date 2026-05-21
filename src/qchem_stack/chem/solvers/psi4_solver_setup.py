"""Geometry, SCF options, and driver metadata for :class:`Psi4IntegralSolver`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.integration.driver_meta import (
    binding_mean_field_scf,
    merge_integration_driver_meta,
)
from qchem_stack.chem.solvers.psi4_solver_common import psi4_version_or_unknown
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config.scf_helpers import (
    resolve_scf_chkfile,
    resolve_scf_density_fit,
    resolve_scf_density_fit_auxbasis,
    resolve_scf_diis_space_dimension,
    resolve_scf_init_guess,
    resolve_scf_level_shift,
    resolve_scf_max_cycle,
    resolve_scf_use_newton,
)

if TYPE_CHECKING:
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver
    from qchem_stack.config import ChemistryExtendedSpec, ExperimentConfig


def normalize_coords_bohr(coords_bohr: np.ndarray) -> np.ndarray:
    geom = np.asarray(coords_bohr, dtype=float)
    if geom.ndim != 2 or geom.shape[1] != 3:
        raise ValueError("coords_bohr_shape_invalid")
    return geom


def validate_symbols_coords(symbols: list[str], coords_bohr: np.ndarray) -> None:
    if len(symbols) != int(coords_bohr.shape[0]):
        raise ValueError("symbol_count_coords_mismatch")


def psi4_geometry_block(
    *, charge: int, multiplicity: int, symbols: list[str], coords_bohr: np.ndarray
) -> str:
    c = coords_bohr.reshape(-1, 3)
    lines = [f"{int(charge)} {int(multiplicity)}"]
    for sym, row in zip(symbols, c, strict=True):
        lines.append(f"{sym} {float(row[0]):.12f} {float(row[1]):.12f} {float(row[2]):.12f}")
    lines.extend(["units bohr", "symmetry c1"])
    return "\n".join(lines)


def method_to_psi4_reference(method: str) -> str:
    m = str(method).strip().upper()
    if m == "RHF":
        return "rhf"
    if m == "ROHF":
        return "rohf"
    if m == "UHF":
        return "uhf"
    raise ValueError(f"Unsupported scf.method for Psi4: {method!r}")


def psi4_scf_options(
    *,
    basis: str,
    method: str,
    max_cycle: int | None,
    chemistry_extended: ChemistryExtendedSpec,
) -> dict[str, Any]:
    opts: dict[str, Any] = {
        "basis": str(basis),
        "reference": method_to_psi4_reference(method),
    }
    if max_cycle is not None:
        opts["maxiter"] = int(max_cycle)
    if chemistry_extended.solvent.model == "ddcosmo":
        opts["pcm"] = True
        opts["pcm_dielectric"] = float(chemistry_extended.solvent.epsilon)
    return opts


def validate_cfg_driver_and_method(cfg: ExperimentConfig) -> None:
    if str(cfg.scf.driver).strip().lower() != "psi4":
        raise ValueError(
            f"Psi4IntegralSolver requires cfg.scf.driver='psi4' (got {cfg.scf.driver!r})."
        )
    if str(cfg.scf.method).upper() not in ("RHF", "ROHF", "UHF"):
        raise ValueError("Psi4IntegralSolver supports scf.method in {RHF, ROHF, UHF}.")


def molecular_system_from_config(cfg: ExperimentConfig) -> MolecularSystem:
    m = cfg.molecule
    return MolecularSystem(
        symbols=m.symbols,
        coordinates_bohr=np.asarray(m.coordinates_in_bohr(), dtype=float),
        charge=m.charge,
        multiplicity=m.multiplicity,
        basis=m.basis,
        ecp=m.ecp,
    )


def base_driver_meta(
    solver: Psi4IntegralSolver,
    *,
    reason: str | None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    scf = solver._cfg.scf
    meta: dict[str, Any] = {
        "driver_meta_schema_version": 1,
        "driver_family": "psi4",
        "scf_method": str(solver._method),
        "upstream_classical_software_tag": "psi4",
        "integral_representation": "psi4_wavefunction",
        "psi4_energy_reason": reason,
        "psi4_version": psi4_version_or_unknown(),
        "ecp": solver._system.ecp,
        "scf_max_cycle": (
            int(resolve_scf_max_cycle(scf)) if resolve_scf_max_cycle(scf) is not None else None
        ),
        "scf_chkfile": resolve_scf_chkfile(scf),
        "scf_init_guess": resolve_scf_init_guess(scf),
        "scf_level_shift": (
            float(resolve_scf_level_shift(scf))
            if resolve_scf_level_shift(scf) is not None
            else None
        ),
        "scf_use_newton": bool(resolve_scf_use_newton(scf)),
        "scf_diis_space_dimension": (
            int(resolve_scf_diis_space_dimension(scf))
            if resolve_scf_diis_space_dimension(scf) is not None
            else None
        ),
        "scf_density_fit": bool(resolve_scf_density_fit(scf)),
        "scf_density_fit_auxbasis": (
            str(resolve_scf_density_fit_auxbasis(scf))
            if resolve_scf_density_fit_auxbasis(scf)
            else None
        ),
    }
    if extra:
        meta.update(extra)
    return merge_integration_driver_meta(
        meta,
        backend_tag="psi4",
        driver_family="psi4",
        kernel_bindings=[
            binding_mean_field_scf("psi4", "psi4_energy_scf_v1", native=True),
        ],
        epistemic_bound=(
            "Psi4 SCF is native; AVAS, NEVPT2, and some CASCI paths may use PySCF kernels "
            "on imported MO coefficients (see driver_meta.kernel_bindings)."
        ),
    )

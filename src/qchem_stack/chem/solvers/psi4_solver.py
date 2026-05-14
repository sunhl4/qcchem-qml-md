"""Psi4 backend scaffold (phase W9–W10).

The registry accepts ``scf.driver=psi4`` so cross-backend plumbing can evolve without
changing YAML shape. Numeric mean-field wiring is gated behind an optional PSI4 install
and must not break default CI (PySCF-only environments).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ExperimentConfig


def _psi4_geometry_block(
    *, charge: int, multiplicity: int, symbols: list[str], coords_bohr: np.ndarray
) -> str:
    c = coords_bohr.reshape(-1, 3)
    lines = [f"{int(charge)} {int(multiplicity)}"]
    for sym, row in zip(symbols, c, strict=True):
        lines.append(f"{sym} {float(row[0])} {float(row[1])} {float(row[2])}")
    lines.extend(["units bohr", "symmetry c1"])
    return "\n".join(lines)


def psi4_hf_total_energy_au(
    *,
    symbols: list[str],
    coords_bohr: np.ndarray,
    charge: int,
    multiplicity: int,
    basis: str,
) -> tuple[float | None, str | None]:
    """Run restricted Hartree–Fock with Psi4 if the Python bindings are installed.

    Returns ``(energy_hartree, None)`` on success or ``(None, reason_string)``.
    """
    geom = np.asarray(coords_bohr, dtype=float)
    if geom.ndim != 2 or geom.shape[1] != 3:
        return None, "coords_bohr_shape_invalid"
    if len(symbols) != geom.shape[0]:
        return None, "symbol_count_coords_mismatch"
    try:
        import psi4
    except ImportError:
        return None, "psi4_import_missing"
    try:
        geom_block = _psi4_geometry_block(
            charge=int(charge),
            multiplicity=int(multiplicity),
            symbols=list(symbols),
            coords_bohr=geom,
        )
        mol = psi4.geometry(geom_block)
        psi4.set_options({"basis": basis})
        e_au = float(psi4.energy("scf", molecule=mol))
        return e_au, None
    except Exception as exc:  # noqa: BLE001
        return None, f"{type(exc).__name__}: {exc}"


class Psi4IntegralSolver:
    """Second classical backend stub (registry + capabilities only in v1)."""

    def __init__(self, cfg: ExperimentConfig) -> None:
        self._cfg = cfg
        m = cfg.molecule
        self._system = MolecularSystem(
            symbols=m.symbols,
            coordinates_bohr=np.asarray(m.coordinates_in_bohr(), dtype=float),
            charge=m.charge,
            multiplicity=m.multiplicity,
            basis=m.basis,
            ecp=m.ecp,
        )

    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            backend_id="psi4",
            supports_molecular_scf=True,
            supports_pbc_scf=False,
            supports_rhf=True,
            supports_rohf=False,
            supports_uhf=False,
            supports_implicit_solvent_ddcosmo=False,
            supports_qmmm=False,
            supports_restricted_active_space_qubit_hamiltonian=False,
            supports_projection_fragment_mulliken_hamiltonian=False,
            supports_schmidt_atomic_hamiltonian=False,
            supports_embedding_input_ao_lowdin=False,
            supports_casscf_orbital_audit=False,
            supports_avas_active_space_projection=False,
            supports_rdm_correction_hooks=False,
            supports_rdm_nevpt2_casci=False,
            supports_get_integrals=False,
        )

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        """Re-bind from experiment config (Tangelo ``set_physical_data`` analog)."""
        if str(cfg.scf.driver).strip().lower() != "psi4":
            raise ValueError(
                "Psi4IntegralSolver.set_physical_data requires cfg.scf.driver='psi4' "
                f"(got {cfg.scf.driver!r})."
            )
        if cfg.scf.method != "RHF":
            raise ValueError("Psi4IntegralSolver scaffold requires scf.method=RHF today.")
        self._cfg = cfg
        m = cfg.molecule
        self._system = MolecularSystem(
            symbols=m.symbols,
            coordinates_bohr=np.asarray(m.coordinates_in_bohr(), dtype=float),
            charge=m.charge,
            multiplicity=m.multiplicity,
            basis=m.basis,
            ecp=m.ecp,
        )

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "Psi4IntegralSolver.get_integrals is not implemented yet (M2+ full-backend milestone)."
        )

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        """Tangelo ``compute_mean_field`` analog (Psi4 numerical SCF is still a stub)."""
        if periodic:
            return self.run_periodic_mean_field()
        return self.run_molecular_mean_field()

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> Psi4IntegralSolver:
        if cfg.scf.method != "RHF":
            raise ValueError("Psi4IntegralSolver scaffold requires scf.method=RHF today.")
        inst = cls(cfg)
        inst.set_physical_data(cfg)
        return inst

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        """Run Psi4 RHF when bindings are available (optional environment)."""
        e_au, reason = psi4_hf_total_energy_au(
            symbols=list(self._system.symbols),
            coords_bohr=np.asarray(self._system.coordinates_bohr, dtype=float),
            charge=int(self._system.charge),
            multiplicity=int(self._system.multiplicity),
            basis=str(self._system.basis),
        )
        if e_au is None:
            raise RuntimeError(f"Psi4 SCF unavailable: {reason}")
        return MolecularMeanFieldResult(
            mf={
                "backend": "psi4",
                "method": "RHF",
                "basis": str(self._system.basis),
                "status": "energy_only_stub",
            },
            e_tot=float(e_au),
            mo_energy=np.asarray([float(e_au)], dtype=float),
            driver_meta={
                "driver_meta_schema_version": 1,
                "driver_family": "psi4",
                "scf_method": "RHF",
                "upstream_classical_software_tag": "psi4",
                "integral_representation": "unknown_energy_only_stub",
                "psi4_energy_reason": None,
            },
        )

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError("Psi4IntegralSolver does not implement PBC.")

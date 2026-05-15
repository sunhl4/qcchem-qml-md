"""Psi4 backend adapter (optional dependency, RHF-only for now).

This module keeps ``scf.driver=psi4`` wiring alive in environments where Psi4 may
not be installed. Runtime behavior mirrors the PySCF adapter shape (set/bind config,
run mean-field, surface driver metadata), while preserving a conservative capability
surface for the current milestone.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ExperimentConfig


def psi4_version_or_unknown() -> str:
    try:
        import psi4

        v = getattr(psi4, "__version__", "")
        if isinstance(v, str) and v.strip():
            return v.strip()
    except Exception:  # pragma: no cover
        pass
    return "unknown"


def _normalize_coords_bohr(coords_bohr: np.ndarray) -> np.ndarray:
    geom = np.asarray(coords_bohr, dtype=float)
    if geom.ndim != 2 or geom.shape[1] != 3:
        raise ValueError("coords_bohr_shape_invalid")
    return geom


def _validate_symbols_coords(symbols: list[str], coords_bohr: np.ndarray) -> None:
    if len(symbols) != int(coords_bohr.shape[0]):
        raise ValueError("symbol_count_coords_mismatch")


def _scf_energy_with_wavefunction(
    *,
    symbols: list[str],
    coords_bohr: np.ndarray,
    charge: int,
    multiplicity: int,
    basis: str,
    method: str,
    max_cycle: int | None,
) -> tuple[float | None, np.ndarray | None, str | None]:
    """Run Psi4 SCF and return ``(e_tot, mo_energy, reason)``.

    ``reason`` is ``None`` on success and a stable string token on failure.
    """
    try:
        geom = _normalize_coords_bohr(coords_bohr)
        _validate_symbols_coords(symbols, geom)
    except ValueError as exc:
        return None, None, str(exc)

    try:
        import psi4
    except ImportError:
        return None, None, "psi4_import_missing"

    try:
        psi4.core.clean()
        psi4.core.clean_options()
        geom_block = _psi4_geometry_block(
            charge=int(charge),
            multiplicity=int(multiplicity),
            symbols=list(symbols),
            coords_bohr=geom,
        )
        mol = psi4.geometry(geom_block)
        psi4.set_options(_psi4_scf_options(basis=basis, method=method, max_cycle=max_cycle))
        e_au, wfn = psi4.energy("scf", molecule=mol, return_wfn=True)
        mo = np.asarray([float(e_au)], dtype=float)
        try:
            eps_a = wfn.epsilon_a()
            if hasattr(eps_a, "np"):
                mo = np.asarray(eps_a.np, dtype=float)
        except Exception:
            pass
        return float(e_au), mo, None
    except Exception as exc:  # noqa: BLE001
        return None, None, f"{type(exc).__name__}: {exc}"


def _psi4_geometry_block(
    *, charge: int, multiplicity: int, symbols: list[str], coords_bohr: np.ndarray
) -> str:
    c = coords_bohr.reshape(-1, 3)
    lines = [f"{int(charge)} {int(multiplicity)}"]
    for sym, row in zip(symbols, c, strict=True):
        lines.append(f"{sym} {float(row[0]):.12f} {float(row[1]):.12f} {float(row[2]):.12f}")
    lines.extend(["units bohr", "symmetry c1"])
    return "\n".join(lines)


def _psi4_scf_options(*, basis: str, method: str, max_cycle: int | None) -> dict[str, Any]:
    opts: dict[str, Any] = {"basis": str(basis), "reference": str(method).lower()}
    if max_cycle is not None:
        opts["maxiter"] = int(max_cycle)
    return opts


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
    e_au, _, reason = _scf_energy_with_wavefunction(
        symbols=list(symbols),
        coords_bohr=np.asarray(coords_bohr, dtype=float),
        charge=int(charge),
        multiplicity=int(multiplicity),
        basis=str(basis),
        method="RHF",
        max_cycle=None,
    )
    return e_au, reason


class Psi4IntegralSolver:
    """Psi4-backed classical solver adapter (RHF molecular branch in current milestone)."""

    def __init__(self, cfg: ExperimentConfig) -> None:
        self._validate_cfg_driver_and_method(cfg)
        self._cfg = cfg
        self._system = self._molecular_system_from_config(cfg)
        self._method = str(cfg.scf.method).upper()

    @staticmethod
    def _molecular_system_from_config(cfg: ExperimentConfig) -> MolecularSystem:
        m = cfg.molecule
        return MolecularSystem(
            symbols=m.symbols,
            coordinates_bohr=np.asarray(m.coordinates_in_bohr(), dtype=float),
            charge=m.charge,
            multiplicity=m.multiplicity,
            basis=m.basis,
            ecp=m.ecp,
        )

    @staticmethod
    def _validate_cfg_driver_and_method(cfg: ExperimentConfig) -> None:
        if str(cfg.scf.driver).strip().lower() != "psi4":
            raise ValueError(
                "Psi4IntegralSolver.set_physical_data requires cfg.scf.driver='psi4' "
                f"(got {cfg.scf.driver!r})."
            )
        if str(cfg.scf.method).upper() != "RHF":
            raise ValueError("Psi4IntegralSolver scaffold requires scf.method=RHF today.")

    def _base_driver_meta(self, *, reason: str | None) -> dict[str, Any]:
        return {
            "driver_meta_schema_version": 1,
            "driver_family": "psi4",
            "scf_method": str(self._method),
            "upstream_classical_software_tag": "psi4",
            "integral_representation": "unknown_energy_only_stub",
            "psi4_energy_reason": reason,
            "psi4_version": psi4_version_or_unknown(),
            "ecp": self._system.ecp,
            "scf_max_cycle": (
                int(self._cfg.scf.max_cycle) if self._cfg.scf.max_cycle is not None else None
            ),
            "scf_chkfile": self._cfg.scf.chkfile,
            "scf_init_guess": self._cfg.scf.init_guess,
            "scf_level_shift": (
                float(self._cfg.scf.level_shift) if self._cfg.scf.level_shift is not None else None
            ),
            "scf_use_newton": bool(self._cfg.scf.use_newton),
            "scf_diis_space_dimension": (
                int(self._cfg.scf.diis_space_dimension)
                if self._cfg.scf.diis_space_dimension is not None
                else None
            ),
            "scf_density_fit": bool(self._cfg.scf.density_fit),
            "scf_density_fit_auxbasis": (
                str(self._cfg.scf.density_fit_auxbasis)
                if self._cfg.scf.density_fit_auxbasis
                else None
            ),
        }

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
        self._validate_cfg_driver_and_method(cfg)
        self._cfg = cfg
        self._system = self._molecular_system_from_config(cfg)
        self._method = str(cfg.scf.method).upper()

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "Psi4IntegralSolver.get_integrals is not implemented yet (M2+ full-backend milestone)."
        )

    def build_embedding_input_system(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        representation: str,
    ) -> dict[str, Any]:
        raise NotImplementedError(
            "Psi4IntegralSolver does not implement AO/Lowdin embedding_input payloads."
        )

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        """Tangelo ``compute_mean_field`` analog (Psi4 numerical SCF is still a stub)."""
        if periodic:
            return self.run_periodic_mean_field()
        return self.run_molecular_mean_field()

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> Psi4IntegralSolver:
        cls._validate_cfg_driver_and_method(cfg)
        return cls(cfg)

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        """Run Psi4 RHF when bindings are available (optional environment)."""
        e_au, mo_energies, reason = _scf_energy_with_wavefunction(
            symbols=list(self._system.symbols),
            coords_bohr=np.asarray(self._system.coordinates_bohr, dtype=float),
            charge=int(self._system.charge),
            multiplicity=int(self._system.multiplicity),
            basis=str(self._system.basis),
            method=str(self._method),
            max_cycle=self._cfg.scf.max_cycle,
        )
        if e_au is None:
            raise RuntimeError(f"Psi4 SCF unavailable: {reason}")
        if mo_energies is None:
            mo_energies = np.asarray([float(e_au)], dtype=float)
        return MolecularMeanFieldResult(
            mf={
                "backend": "psi4",
                "method": str(self._method),
                "basis": str(self._system.basis),
                "status": "energy_only_stub",
            },
            e_tot=float(e_au),
            mo_energy=np.asarray(mo_energies, dtype=float),
            driver_meta=self._base_driver_meta(reason=None),
        )

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError("Psi4IntegralSolver does not implement PBC.")

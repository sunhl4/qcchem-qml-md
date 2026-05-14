from __future__ import annotations

from typing import Any, Literal

import numpy as np

from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ChemistryExtendedSpec, ExperimentConfig


def require_pyscf() -> tuple[Any, Any]:
    try:
        from pyscf import gto, scf
    except ImportError as e:  # pragma: no cover
        raise ImportError("PySCF is required. Install with: pip install qchem-stack[chem]") from e
    return gto, scf


def pyscf_version_or_unknown() -> str:
    try:
        import pyscf

        v = getattr(pyscf, "__version__", "")
        if isinstance(v, str) and v.strip():
            return v.strip()
    except Exception:  # pragma: no cover
        pass
    return "unknown"


class PySCFIntegralSolver:
    """PySCF implementation of :class:`~qchem_stack.chem.solvers.base.ChemIntegralSolver`."""

    def __init__(
        self,
        system: MolecularSystem,
        method: Literal["RHF", "ROHF", "UHF"],
        chemistry_extended: ChemistryExtendedSpec,
        *,
        scf_max_cycle: int | None = None,
        chkfile: str | None = None,
        init_guess: str | None = None,
        level_shift: float | None = None,
        use_newton: bool = False,
        diis_space_dimension: int | None = None,
        density_fit: bool = False,
        density_fit_auxbasis: str | None = None,
    ) -> None:
        self.system = system
        self.method = method
        self.chemistry_extended = chemistry_extended
        self.scf_max_cycle = scf_max_cycle
        self.chkfile = chkfile
        self.init_guess = init_guess
        self.level_shift = level_shift
        self.use_newton = use_newton
        self.diis_space_dimension = diis_space_dimension
        self.density_fit = density_fit
        self.density_fit_auxbasis = density_fit_auxbasis

    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            backend_id="pyscf",
            supports_molecular_scf=True,
            supports_pbc_scf=True,
            supports_rhf=True,
            supports_rohf=True,
            supports_uhf=True,
            supports_implicit_solvent_ddcosmo=True,
            supports_qmmm=False,
            supports_restricted_active_space_qubit_hamiltonian=True,
            supports_projection_fragment_mulliken_hamiltonian=True,
            supports_schmidt_atomic_hamiltonian=True,
            supports_embedding_input_ao_lowdin=True,
            supports_casscf_orbital_audit=True,
            supports_avas_active_space_projection=True,
            supports_rdm_correction_hooks=True,
            supports_rdm_nevpt2_casci=True,
            supports_get_integrals=True,
        )

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> PySCFIntegralSolver:
        m = cfg.molecule
        sys = MolecularSystem(
            symbols=m.symbols,
            coordinates_bohr=np.asarray(m.coordinates_in_bohr(), dtype=float),
            charge=m.charge,
            multiplicity=m.multiplicity,
            basis=m.basis,
            ecp=m.ecp,
        )
        scf = cfg.scf
        inst = cls(
            sys,
            method=scf.method,
            chemistry_extended=cfg.chemistry_extended,
            scf_max_cycle=scf.max_cycle,
            chkfile=scf.chkfile,
            init_guess=scf.init_guess,
            level_shift=scf.level_shift,
            use_newton=scf.use_newton,
            diis_space_dimension=scf.diis_space_dimension,
            density_fit=scf.density_fit,
            density_fit_auxbasis=scf.density_fit_auxbasis,
        )
        inst.set_physical_data(cfg)
        return inst

    def _scf_control_meta(self) -> dict[str, Any]:
        return {
            "scf_chkfile": self.chkfile,
            "scf_init_guess": self.init_guess,
            "scf_level_shift": float(self.level_shift) if self.level_shift is not None else None,
            "scf_use_newton": bool(self.use_newton),
            "scf_diis_space_dimension": (
                int(self.diis_space_dimension) if self.diis_space_dimension is not None else None
            ),
            "scf_density_fit": bool(self.density_fit),
            "scf_density_fit_auxbasis": str(self.density_fit_auxbasis)
            if self.density_fit_auxbasis
            else None,
        }

    def _make_mol(self, gto: Any) -> Any:
        parts = []
        for sym, xyz in zip(self.system.symbols, self.system.coordinates_bohr, strict=True):
            parts.append(f"{sym} {float(xyz[0]):.12f} {float(xyz[1]):.12f} {float(xyz[2]):.12f}")
        atom = "; ".join(parts)
        symm_kw: dict[str, Any] = {}
        symm = self.chemistry_extended.pyscf_symmetry
        if symm is not False and symm is not None:
            if isinstance(symm, str):
                if not str(symm).strip():
                    raise ValueError("chemistry_extended.pyscf_symmetry string must be non-empty.")
                symm_kw["symmetry"] = str(symm)
            else:
                symm_kw["symmetry"] = bool(symm)
        return gto.M(
            atom=atom,
            basis=self.system.basis,
            ecp=self.system.ecp,
            charge=self.system.charge,
            spin=self.system.multiplicity - 1,
            unit="Bohr",
            **symm_kw,
        )

    def _base_driver_meta(
        self,
        *,
        pbc: bool,
        pbc_kpoint_mesh: list[int] | None,
        pbc_active_space_kpoint_index: int | None,
    ) -> dict[str, Any]:
        solv = self.chemistry_extended.solvent_model
        meta: dict[str, Any] = {
            "driver_meta_schema_version": 1,
            "driver_family": "pyscf",
            "scf_method": self.method,
            "integral_representation": "mo",
            "solvent_model": str(solv),
            "ddcosmo_epsilon": float(self.chemistry_extended.ddcosmo_epsilon)
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
            "pyscf_symmetry": self.chemistry_extended.pyscf_symmetry,
            "ecp": self.system.ecp,
        }
        meta.update(self._scf_control_meta())
        return meta

    def _apply_scf_controls(self, mf: Any, *, chkfile_present: bool) -> None:
        if self.chkfile:
            mf.chkfile = self.chkfile
        if self.scf_max_cycle is not None:
            mf.max_cycle = int(self.scf_max_cycle)
        if self.init_guess is not None:
            mf.init_guess = self.init_guess
        elif self.chkfile:
            mf.init_guess = "chkfile" if chkfile_present else "minao"
        if self.level_shift is not None and hasattr(mf, "level_shift"):
            mf.level_shift(float(self.level_shift))
        if self.diis_space_dimension is not None and hasattr(mf, "diis_space"):
            mf.diis_space = int(self.diis_space_dimension)

    def _build_mean_field_factory(self, gto_mod: Any, scf_mod: Any) -> Any:
        mol = self._make_mol(gto_mod)
        if self.method == "RHF":
            mf = scf_mod.RHF(mol)
        elif self.method == "ROHF":
            mf = scf_mod.ROHF(mol)
        else:
            mf = scf_mod.UHF(mol)
        if self.use_newton and self.method in ("RHF", "ROHF") and hasattr(mf, "newton"):
            mf = mf.newton()
        if self.chemistry_extended.solvent_model == "ddcosmo":
            from pyscf import solvent

            mf = solvent.ddCOSMO(mf)
            mf.with_solvent.eps = float(self.chemistry_extended.ddcosmo_epsilon)
        if self.density_fit and hasattr(mf, "density_fit"):
            if self.density_fit_auxbasis:
                mf = mf.density_fit(auxbasis=self.density_fit_auxbasis)
            else:
                mf = mf.density_fit()
        return mf

    def build_molecular_mf_without_kernel(self) -> Any:
        gto, scf = require_pyscf()
        mf = self._build_mean_field_factory(gto, scf)
        import os

        chk_present = bool(self.chkfile and os.path.isfile(self.chkfile))
        self._apply_scf_controls(mf, chkfile_present=chk_present)
        return mf

    def idle_molecular_driver_meta(self) -> dict[str, Any]:
        """Driver metadata aligned with :meth:`compute_mean_field` (molecular branch) before ``mf.kernel()``."""
        meta = self._base_driver_meta(
            pbc=False,
            pbc_kpoint_mesh=None,
            pbc_active_space_kpoint_index=None,
        )
        if self.chemistry_extended.solvent_model == "ddcosmo":
            meta["solvent"] = "ddcosmo"
            meta["ddcosmo_epsilon"] = float(self.chemistry_extended.ddcosmo_epsilon)
        return meta

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        """Re-bind physical system and SCF controls (Tangelo ``set_physical_data`` analog)."""
        if str(cfg.scf.driver).strip().lower() != "pyscf":
            raise ValueError(
                "PySCFIntegralSolver.set_physical_data requires cfg.scf.driver='pyscf' "
                f"(got {cfg.scf.driver!r})."
            )
        m = cfg.molecule
        self.system = MolecularSystem(
            symbols=m.symbols,
            coordinates_bohr=np.asarray(m.coordinates_in_bohr(), dtype=float),
            charge=m.charge,
            multiplicity=m.multiplicity,
            basis=m.basis,
            ecp=m.ecp,
        )
        scf = cfg.scf
        self.method = scf.method
        self.chemistry_extended = cfg.chemistry_extended
        self.scf_max_cycle = scf.max_cycle
        self.chkfile = scf.chkfile
        self.init_guess = scf.init_guess
        self.level_shift = scf.level_shift
        self.use_newton = scf.use_newton
        self.diis_space_dimension = scf.diis_space_dimension
        self.density_fit = scf.density_fit
        self.density_fit_auxbasis = scf.density_fit_auxbasis

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """
        Return active-space MO integrals on the PySCF CASCI path.

        Required kwargs:
        - ``n_active_orbitals`` (alias ``ncas``)
        - ``n_active_electrons`` (alias ``nelecas``)

        Optional kwargs:
        - ``frozen_orbitals``: list[int]
        - ``run_scf``: bool (default True)
        """
        from pyscf import ao2mo, mcscf

        from qchem_stack.chem.integral_convention import (
            spatial_mo_eri_pyscf_to_openfermion_mo_ordering,
        )

        ncas_raw = kwargs.get("n_active_orbitals", kwargs.get("ncas"))
        nele_raw = kwargs.get("n_active_electrons", kwargs.get("nelecas"))
        if ncas_raw is None or nele_raw is None:
            raise ValueError(
                "get_integrals requires n_active_orbitals/n_active_electrons "
                "(aliases: ncas/nelecas)."
            )
        ncas = int(ncas_raw)
        nelecas = int(nele_raw)
        if ncas <= 0 or nelecas <= 0:
            raise ValueError("n_active_orbitals and n_active_electrons must be positive integers.")
        if self.method not in ("RHF", "ROHF"):
            raise NotImplementedError(
                f"get_integrals currently supports RHF/ROHF only (got method={self.method!r})."
            )

        run_scf = bool(kwargs.get("run_scf", True))
        mf = self.build_molecular_mf_without_kernel()
        if run_scf:
            mf.kernel()
        if not getattr(mf, "converged", False):
            raise RuntimeError("SCF did not converge; cannot build active-space integrals.")
        mo = np.asarray(mf.mo_coeff, dtype=float)
        cas = mcscf.CASCI(mf, ncas, nelecas)
        frozen = kwargs.get("frozen_orbitals")
        if frozen is not None:
            if not isinstance(frozen, (list, tuple)):
                raise TypeError("frozen_orbitals must be a list/tuple of orbital indices.")
            cas.frozen = sorted(set(int(i) for i in frozen))
        h1, e_core = cas.get_h1eff(mo)
        h2 = cas.get_h2eff(mo)
        h1a = np.asarray(h1)
        h2a = np.asarray(h2)
        # PySCF's ao2mo.restore only accepts real-valued ERI tensors.
        if h2a.ndim != 4:
            h2_restore_input = h2a
            if np.iscomplexobj(h2_restore_input):
                if np.max(np.abs(h2_restore_input.imag)) > 1e-7:
                    raise ValueError("Active-space integrals have non-trivial imaginary part.")
                h2_restore_input = np.asarray(h2_restore_input.real, dtype=float)
            h2a = np.asarray(ao2mo.restore(1, h2_restore_input, ncas))
        if np.max(np.abs(h1a.imag)) > 1e-7 or np.max(np.abs(h2a.imag)) > 1e-7:
            raise ValueError("Active-space integrals have non-trivial imaginary part.")
        h1_real = np.asarray(h1a.real, dtype=float)
        h2_chemist = np.asarray(h2a.real, dtype=float)
        h2_openfermion = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(h2_chemist)

        return {
            "schema": "pyscf_active_space_integrals_v1",
            "backend_id": "pyscf",
            "integral_representation": "mo",
            "constant": float(e_core),
            "n_active_orbitals": ncas,
            "n_active_electrons": nelecas,
            "h1_spatial_mo": h1_real,
            "h2_spatial_mo_chemist": h2_chemist,
            "h2_spatial_mo_openfermion": h2_openfermion,
            "openfermion_bridge": "pyscf_tangelo_openfermion_v1",
            "scf_energy": float(mf.e_tot),
            "pyscf_converged": bool(getattr(mf, "converged", False)),
        }

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        """Tangelo ``compute_mean_field`` analog (molecule vs periodic)."""
        return (
            self._execute_periodic_mean_field()
            if periodic
            else self._execute_molecular_mean_field()
        )

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        return self.compute_mean_field(periodic=False)

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        return self.compute_mean_field(periodic=True)

    def _execute_molecular_mean_field(self) -> MolecularMeanFieldResult:
        if self.chemistry_extended.pbc_cell_vectors_bohr is not None:
            raise ValueError(
                "molecular branch requires a non-PBC config; use compute_mean_field(periodic=True)."
            )
        gto, scf = require_pyscf()
        mf = self._build_mean_field_factory(gto, scf)
        import os

        chk_present = bool(self.chkfile and os.path.isfile(self.chkfile))
        self._apply_scf_controls(mf, chkfile_present=chk_present)
        meta = self._base_driver_meta(
            pbc=False,
            pbc_kpoint_mesh=None,
            pbc_active_space_kpoint_index=None,
        )
        if self.chemistry_extended.solvent_model == "ddcosmo":
            meta["solvent"] = "ddcosmo"
            meta["ddcosmo_epsilon"] = float(self.chemistry_extended.ddcosmo_epsilon)
        e = float(mf.kernel())
        return MolecularMeanFieldResult(
            mf=mf,
            e_tot=e,
            mo_energy=np.asarray(mf.mo_energy, dtype=float),
            driver_meta=meta,
        )

    def _execute_periodic_mean_field(self) -> MolecularMeanFieldResult:
        pbc = self.chemistry_extended.pbc_cell_vectors_bohr
        if pbc is None:
            raise ValueError("periodic branch requires chemistry_extended.pbc_cell_vectors_bohr")
        if self.method != "RHF":
            raise ValueError("PBC branch requires scf.method=RHF (KRHF/k-mesh).")
        try:
            from pyscf.pbc import gto as pbc_gto
            from pyscf.pbc import scf as pbc_scf
        except ImportError as e:  # pragma: no cover
            raise ImportError("PySCF with pbc is required.") from e
        cell = self._make_pbc_cell(pbc_gto)
        cell.build()
        mesh = list(self.chemistry_extended.pbc_kpoint_mesh)
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

        import os

        chk_present = bool(self.chkfile and os.path.isfile(self.chkfile))
        self._apply_scf_controls(mf, chkfile_present=chk_present)

        meta = self._base_driver_meta(
            pbc=True,
            pbc_kpoint_mesh=mesh,
            pbc_active_space_kpoint_index=int(
                self.chemistry_extended.pbc_active_space_kpoint_index
            ),
        )
        meta.update(
            {
                "gamma_only": not use_k,
                "n_kpoints": n_k,
                "cell_vectors_bohr": [list(map(float, row)) for row in pbc],
            }
        )
        if self.chemistry_extended.pbc_active_space_kpoint_index >= n_k:
            raise ValueError(
                f"pbc_active_space_kpoint_index={self.chemistry_extended.pbc_active_space_kpoint_index} "
                f"out of range for n_kpoints={n_k}"
            )
        if self.chemistry_extended.solvent_model == "ddcosmo":
            from pyscf import solvent

            try:
                mf = solvent.ddCOSMO(mf)
                mf.with_solvent.eps = float(self.chemistry_extended.ddcosmo_epsilon)
                meta["solvent"] = "ddcosmo"
                meta["ddcosmo_epsilon"] = float(self.chemistry_extended.ddcosmo_epsilon)
            except Exception as e:  # noqa: BLE001
                raise RuntimeError("ddCOSMO on this periodic mean-field object failed.") from e
        e = float(mf.kernel())
        mo_ev = mf.mo_energy
        if isinstance(mo_ev, (list, tuple)):
            ik = int(self.chemistry_extended.pbc_active_space_kpoint_index)
            mo_e_out = np.asarray(mo_ev[ik], dtype=float)
        else:
            mo_e_out = np.asarray(mo_ev, dtype=float)
        return MolecularMeanFieldResult(
            mf=mf,
            e_tot=e,
            mo_energy=mo_e_out,
            driver_meta=meta,
        )

    def _make_pbc_cell(self, gto_pbc: Any) -> Any:
        pbc = self.chemistry_extended.pbc_cell_vectors_bohr
        assert pbc is not None
        a = np.asarray(pbc, dtype=float)
        parts = []
        for sym, xyz in zip(self.system.symbols, self.system.coordinates_bohr, strict=True):
            parts.append(f"{sym} {float(xyz[0]):.12f} {float(xyz[1]):.12f} {float(xyz[2]):.12f}")
        atom = "; ".join(parts)
        return gto_pbc.M(
            atom=atom,
            a=a,
            basis=self.system.basis,
            charge=self.system.charge,
            spin=self.system.multiplicity - 1,
            unit="Bohr",
        )

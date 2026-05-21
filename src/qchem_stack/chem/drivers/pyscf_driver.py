"""PySCF compatibility driver facade over :class:`~qchem_stack.chem.solvers.pyscf_solver.PySCFIntegralSolver`.

Implementation map:

| Module | Scope |
|--------|--------|
| ``pyscf_driver_types`` | ``PySCFRHFResult``, unwrap helper |
| ``pyscf_driver_mean_field`` | Molecular / PBC mean-field runs |
| ``pyscf_driver_mo`` | MO reordering, active-space sizing |
| ``pyscf_driver`` (this file) | Class API, one-body ops, quantum problem build |
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, cast

import numpy as np

from qchem_stack.chem.drivers.pyscf_driver_mean_field import (
    mean_field_reference_for_benchmarks,
    run_molecular_mean_field,
    run_pbc_mean_field,
)
from qchem_stack.chem.drivers.pyscf_driver_mo import (
    classify_mean_field_spin_symmetry as _classify_mean_field_spin_symmetry,
)
from qchem_stack.chem.drivers.pyscf_driver_mo import (
    get_ncas_nelec_couplet,
    make_actives_contiguous_columns,
)
from qchem_stack.chem.drivers.pyscf_driver_mo import (
    reorder_molecular_orbitals_columns as _reorder_molecular_orbitals_columns,
)
from qchem_stack.chem.drivers.pyscf_driver_types import (
    PySCFRHFResult,
    unwrap_pyscf_rhf_for_backend_operations,
)
from qchem_stack.chem.integrals.pyscf_lowdin import build_lowdin_system_from_rhf
from qchem_stack.chem.integrals.pyscf_onebody import (
    one_electron_operator_fermion_from_rhf,
    one_electron_operator_pauli_from_rhf,
)
from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.chem.systems.pyscf_views import PySCFAOSystem, PySCFLowdinSystem
from qchem_stack.config import ActiveSpaceSpec, ChemistryExtendedSpec, ExperimentConfig
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
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference


class PySCFDriver:
    """Compatibility facade over :class:`PySCFIntegralSolver` for PySCF-specific workflows."""

    def __init__(
        self,
        system: MolecularSystem,
        method: Literal["RHF", "ROHF", "UHF"] = "RHF",
        chemistry_extended: ChemistryExtendedSpec | None = None,
        *,
        scf_max_cycle: int | None = None,
        chkfile: str | None = None,
        init_guess: str | None = None,
        level_shift: float | None = None,
        use_newton: bool = False,
        diis_space_dimension: int | None = None,
        density_fit: bool = False,
        density_fit_auxbasis: str | None = None,
        active_space: ActiveSpaceSpec | None = None,
        experiment_config: ExperimentConfig | None = None,
    ) -> None:
        self.system = system
        self.method = method
        self.chemistry_extended = chemistry_extended or ChemistryExtendedSpec()
        self.active_space = active_space
        self.experiment_config = experiment_config
        self.scf_max_cycle = scf_max_cycle
        self.chkfile = chkfile
        self.init_guess = init_guess
        self.level_shift = level_shift
        self.use_newton = use_newton
        self.diis_space_dimension = diis_space_dimension
        self.density_fit = density_fit
        self.density_fit_auxbasis = density_fit_auxbasis

    def _integral_solver(self) -> PySCFIntegralSolver:
        return PySCFIntegralSolver(
            self.system,
            cast("Literal['RHF', 'ROHF', 'UHF']", self.method),
            self.chemistry_extended,
            scf_max_cycle=self.scf_max_cycle,
            chkfile=self.chkfile,
            init_guess=self.init_guess,
            level_shift=self.level_shift,
            use_newton=self.use_newton,
            diis_space_dimension=self.diis_space_dimension,
            density_fit=self.density_fit,
            density_fit_auxbasis=self.density_fit_auxbasis,
        )

    @classmethod
    def from_config(cls, cfg: ExperimentConfig) -> PySCFDriver:
        if cfg.scf.driver != "pyscf":
            raise ValueError(
                "PySCFDriver builds OpenFermion Hamiltonians from PySCF mean fields; "
                f"scf.driver must be 'pyscf' for this driver (got {cfg.scf.driver!r}). "
                "Use qchem_stack.chem.solvers.create_solver(cfg) for other backends."
            )
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
        return cls(
            sys,
            method=scf.method,
            chemistry_extended=cfg.chemistry_extended,
            scf_max_cycle=resolve_scf_max_cycle(scf),
            chkfile=resolve_scf_chkfile(scf),
            init_guess=resolve_scf_init_guess(scf),
            level_shift=resolve_scf_level_shift(scf),
            use_newton=resolve_scf_use_newton(scf),
            diis_space_dimension=resolve_scf_diis_space_dimension(scf),
            density_fit=resolve_scf_density_fit(scf),
            density_fit_auxbasis=resolve_scf_density_fit_auxbasis(scf),
            active_space=cfg.active_space,
            experiment_config=cfg,
        )

    def _mean_field_reference_for_benchmarks(
        self,
        rhf: PySCFRHFResult | ClassicalMeanFieldReference | None,
    ) -> ClassicalMeanFieldReference:
        return mean_field_reference_for_benchmarks(self, rhf)

    def _run_mean_field(self) -> PySCFRHFResult:
        return run_molecular_mean_field(self)

    def run_rhf(self) -> PySCFRHFResult:
        return self._run_mean_field()

    def run_rohf(self) -> PySCFRHFResult:
        return self._run_mean_field()

    def run_uhf(self) -> PySCFRHFResult:
        return self._run_mean_field()

    def compute_one_electron_operator_fermion(
        self,
        oper: Literal["kin", "nuc", "hcore", "ovlp", "r", "rr", "dm"],
        *,
        origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
        rhf: PySCFRHFResult | None = None,
    ) -> Any:
        pr = unwrap_pyscf_rhf_for_backend_operations(rhf if rhf is not None else self.run_rhf())
        return one_electron_operator_fermion_from_rhf(pr, oper, origin=origin)

    def compute_one_electron_operator_pauli(
        self,
        oper: Literal["kin", "nuc", "hcore", "ovlp", "r", "rr", "dm"],
        *,
        origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
        fermion_qubit_mapping: Literal[
            "jordan_wigner",
            "bravyi_kitaev",
            "symmetry_conserving_bravyi_kitaev",
        ] = "jordan_wigner",
        n_electrons: int | None = None,
        rhf: PySCFRHFResult | None = None,
    ) -> Any:
        pr = unwrap_pyscf_rhf_for_backend_operations(rhf if rhf is not None else self.run_rhf())
        return one_electron_operator_pauli_from_rhf(
            pr,
            oper,
            origin=origin,
            fermion_qubit_mapping=fermion_qubit_mapping,
            n_electrons=n_electrons,
        )

    @classmethod
    def from_pyscf_mean_field(
        cls,
        mf: Any,
        *,
        molecular_system: MolecularSystem | None = None,
        chemistry_extended: ChemistryExtendedSpec | None = None,
        active_space: ActiveSpaceSpec | None = None,
        experiment_config: ExperimentConfig | None = None,
        inferred_method: Literal["RHF", "ROHF", "UHF"] | None = None,
    ) -> PySCFDriver:

        mol = mf.mol
        if molecular_system is None:
            coords = np.asarray(mol.atom_coords(unit="Bohr"), dtype=float)
            symbols = [mol.atom_symbol(i) for i in range(mol.natm)]
            basis_label = getattr(mol, "basis", None)
            molecular_system = MolecularSystem(
                symbols=list(symbols),
                coordinates_bohr=coords,
                charge=int(mol.charge),
                multiplicity=int(mol.spin) + 1 if mol.spin is not None else 1,
                basis=str(basis_label) if basis_label else "sto-3g",
                ecp=getattr(mol, "ecp", None),
            )
        if inferred_method is None:
            meth = _classify_mean_field_spin_symmetry(mf)
        else:
            meth = inferred_method
        return cls(
            molecular_system,
            method=meth,
            chemistry_extended=chemistry_extended or ChemistryExtendedSpec(),
            active_space=active_space,
            experiment_config=experiment_config,
        )

    classify_mean_field_spin_symmetry = staticmethod(_classify_mean_field_spin_symmetry)
    reorder_molecular_orbitals_columns = staticmethod(_reorder_molecular_orbitals_columns)

    def make_actives_contiguous_columns(
        self,
        mo_coeff: np.ndarray,
        active_molecular_orbital_indices: list[int],
        *,
        frozen_prefix_count: int = 0,
    ) -> tuple[np.ndarray, list[int]]:
        return make_actives_contiguous_columns(
            mo_coeff, active_molecular_orbital_indices, frozen_prefix_count=frozen_prefix_count
        )

    def get_ncas_nelec_couplet(
        self,
        *,
        resolved_reference: ClassicalMeanFieldReference | None = None,
    ) -> tuple[int, int]:
        return get_ncas_nelec_couplet(self, resolved_reference=resolved_reference)

    def get_system_ao(
        self,
        rhf: PySCFRHFResult | None = None,
        *,
        run_hf: bool = True,
    ) -> PySCFAOSystem:
        if self.chemistry_extended.pbc.cell_vectors_bohr is not None:
            raise ValueError("get_system_ao currently supports molecular branch only (non-PBC).")
        if rhf is None and run_hf:
            rhf = self._run_mean_field()
        if rhf is not None:
            meta = dict(rhf.driver_meta)
            meta["integral_representation"] = "ao"
            meta["ao_reference_kind"] = "scf_object"
            meta["ao_run_hf"] = True
            return PySCFAOSystem(
                mf=rhf.mf,
                molecular_system=self.system,
                driver_meta=meta,
                has_run_hf=True,
                e_tot=float(rhf.e_tot),
            )
        solv = self._integral_solver()
        mf = solv.build_molecular_mf_without_kernel()
        meta = dict(solv.idle_molecular_driver_meta())
        if self.chemistry_extended.solvent.model == "ddcosmo":
            meta.setdefault("solvent", "ddcosmo")
            meta.setdefault("ddcosmo_epsilon", float(self.chemistry_extended.solvent.epsilon))
        meta["integral_representation"] = "ao"
        meta["ao_reference_kind"] = "scf_object"
        meta["ao_run_hf"] = False
        return PySCFAOSystem(
            mf=mf,
            molecular_system=self.system,
            driver_meta=meta,
            has_run_hf=False,
            e_tot=None,
        )

    def get_lowdin_system(self, rhf: PySCFRHFResult | None = None) -> PySCFLowdinSystem:
        if self.chemistry_extended.pbc.cell_vectors_bohr is not None:
            raise ValueError(
                "get_lowdin_system currently supports molecular branch only (non-PBC)."
            )
        if rhf is None:
            rhf = self._run_mean_field()
        return build_lowdin_system_from_rhf(rhf, molecular_system=self.system)

    def get_restricted_active_space_quantum_problem(
        self,
        n_active_orbitals: int,
        n_active_electrons: int,
        *,
        fermion_qubit_mapping: Literal[
            "jordan_wigner",
            "bravyi_kitaev",
            "symmetry_conserving_bravyi_kitaev",
        ] = "jordan_wigner",
        rhf: PySCFRHFResult | None = None,
        prefer_restricted_spatial_fermion_for_jordan_wigner: bool | None = None,
        jordan_wigner_coeff_atol: float | None = None,
    ) -> Any:
        from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
        from qchem_stack.chem.molecular_problem import build_restricted_active_space_quantum_problem

        if rhf is None:
            rhf = self.run_rhf()
        reference = ClassicalMeanFieldReference(
            mf=rhf.mf,
            e_tot=float(rhf.e_tot),
            mo_energy=np.asarray(rhf.mo_energy, dtype=float),
            molecular_system=rhf.molecular_system,
            driver_meta=dict(rhf.driver_meta),
        )
        if prefer_restricted_spatial_fermion_for_jordan_wigner is None:
            prefer_eff = (
                bool(self.active_space.jw.prefer_restricted_spatial)
                if self.active_space is not None
                else False
            )
        else:
            prefer_eff = prefer_restricted_spatial_fermion_for_jordan_wigner
        atol_eff = jordan_wigner_coeff_atol
        if atol_eff is None and self.active_space is not None:
            atol_eff = self.active_space.jw.coeff_atol
        return build_restricted_active_space_quantum_problem(
            reference,
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
            fermion_qubit_mapping=fermion_qubit_mapping,
            prefer_restricted_spatial_fermion_for_jordan_wigner=prefer_eff,
            jordan_wigner_coeff_atol=atol_eff,
        )

    def run_classical_benchmarks(
        self,
        rhf: PySCFRHFResult | ClassicalMeanFieldReference | None = None,
        *,
        n_active_orbitals: int | None = None,
        n_active_electrons: int | None = None,
    ) -> dict[str, Any]:
        from qchem_stack.chem.classical_benchmarks import (
            ClassicalBenchmarkContext,
            run_classical_post_hf_benchmarks,
        )

        ref = self._mean_field_reference_for_benchmarks(rhf)
        ctx = ClassicalBenchmarkContext(
            mean_field_reference=ref,
            reference_scf_method=str(self.method),
            n_active_orbitals=n_active_orbitals,
            n_active_electrons=n_active_electrons,
        )
        return run_classical_post_hf_benchmarks(self.experiment_config, ctx)

    def run_pbc_rhf(self) -> PySCFRHFResult:
        return run_pbc_mean_field(self)


__all__ = ["PySCFDriver", "PySCFRHFResult", "unwrap_pyscf_rhf_for_backend_operations"]

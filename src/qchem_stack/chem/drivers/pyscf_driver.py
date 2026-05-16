from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from qchem_stack.chem.integrals.pyscf_active_space import (
    active_space_casci_raw_blocks,
    active_space_integrals,
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

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference


@dataclass
class PySCFRHFResult:
    mf: Any
    e_tot: float
    mo_energy: np.ndarray
    molecular_system: MolecularSystem
    driver_meta: dict[str, Any] = field(default_factory=dict)
    """e.g. ``ddcosmo`` flags — parity with InQuanto-PySCF *surface* (not product parity)."""


def unwrap_pyscf_rhf_for_backend_operations(rhf: PySCFRHFResult) -> PySCFRHFResult:
    """Return a result whose ``mf`` is the raw PySCF object (not a :class:`~qchem_stack.chem.bridges.mean_field_like.MeanFieldLike` wrapper)."""
    mf = rhf.mf
    if hasattr(mf, "raw_handle"):
        raw = mf.raw_handle()
        if raw is not mf:
            return PySCFRHFResult(
                mf=raw,
                e_tot=rhf.e_tot,
                mo_energy=rhf.mo_energy,
                molecular_system=rhf.molecular_system,
                driver_meta=dict(rhf.driver_meta),
            )
    return rhf


class PySCFDriver:
    """Compatibility facade over :class:`PySCFIntegralSolver` for PySCF-specific workflows.

    Main pipeline orchestration should prefer solver-registry + canonical pre-quantum
    handoff objects. Keep this class for explicit PySCF-native helper surfaces
    (AO/Lowdin handles, external MF onboarding, notebooks).
    """

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
            self.method,
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
            scf_max_cycle=scf.max_cycle,
            chkfile=scf.chkfile,
            init_guess=scf.init_guess,
            level_shift=scf.level_shift,
            use_newton=scf.use_newton,
            diis_space_dimension=scf.diis_space_dimension,
            density_fit=scf.density_fit,
            density_fit_auxbasis=scf.density_fit_auxbasis,
            active_space=cfg.active_space,
            experiment_config=cfg,
        )

    def _mean_field_reference_for_benchmarks(
        self,
        rhf: PySCFRHFResult | ClassicalMeanFieldReference | None,
    ) -> ClassicalMeanFieldReference:
        from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference

        if rhf is None:
            pr = self._run_mean_field()
            meta = dict(pr.driver_meta)
            meta.setdefault("upstream_classical_software_tag", "pyscf")
            return ClassicalMeanFieldReference(
                mf=pr.mf,
                e_tot=float(pr.e_tot),
                mo_energy=np.asarray(pr.mo_energy, dtype=float),
                molecular_system=self.system,
                driver_meta=meta,
            )
        if isinstance(rhf, ClassicalMeanFieldReference):
            return rhf
        meta = dict(rhf.driver_meta)
        meta.setdefault("upstream_classical_software_tag", "pyscf")
        return ClassicalMeanFieldReference(
            mf=rhf.mf,
            e_tot=float(rhf.e_tot),
            mo_energy=np.asarray(rhf.mo_energy, dtype=float),
            molecular_system=rhf.molecular_system,
            driver_meta=meta,
        )

    def _run_mean_field(self) -> PySCFRHFResult:
        run = self._integral_solver().compute_mean_field(periodic=False)
        meta = dict(run.driver_meta)
        if self.chemistry_extended.solvent_model == "ddcosmo":
            meta.setdefault("solvent", "ddcosmo")
            meta.setdefault("ddcosmo_epsilon", float(self.chemistry_extended.ddcosmo_epsilon))
        from qchem_stack.chem.bridges.interchange import merge_canonical_classical_bridge_headers

        meta = merge_canonical_classical_bridge_headers(
            meta,
            upstream_software_tag="pyscf",
            periodic_boundary_condition=False,
        )
        return PySCFRHFResult(
            mf=run.mf,
            e_tot=run.e_tot,
            mo_energy=run.mo_energy,
            molecular_system=self.system,
            driver_meta=meta,
        )

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
        """
        Build one-electron fermionic operator(s) in MO basis.

        Returns either a single ``FermionOperator`` (scalar operators) or a list for vector/tensor operators:
        ``r`` / ``dm`` -> length 3, ``rr`` -> length 9.
        """
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
        """
        Map one-electron fermionic operator(s) to qubit-space Pauli operators.
        """
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
        """Build a driver pointing at an existing PySCF ``mf`` (InQuanto ``from_mf``-style onboarding).

        The underlying ``Mol`` geometry / basis seed an internal :class:`MolecularSystem`. ``mf``
        stays live for subsequent AO / Lowdin helpers.
        """
        from pyscf import scf as scf_mod

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
        meth: Literal["RHF", "ROHF", "UHF"]
        if inferred_method is None:
            if isinstance(mf, scf_mod.uhf.UHF):
                meth = "UHF"
            elif isinstance(mf, scf_mod.rohf.ROHF):
                meth = "ROHF"
            else:
                meth = "RHF"
        else:
            meth = inferred_method
        return cls(
            molecular_system,
            method=meth,
            chemistry_extended=chemistry_extended or ChemistryExtendedSpec(),
            active_space=active_space,
            experiment_config=experiment_config,
        )

    @staticmethod
    def classify_mean_field_spin_symmetry(mf: Any) -> Literal["RHF", "ROHF", "UHF"]:
        """Map a PySCF mean-field instance to coarse ``scf.method`` enum labels."""
        from pyscf import scf as scf_mod

        if isinstance(mf, scf_mod.uhf.UHF):
            return "UHF"
        if isinstance(mf, scf_mod.rohf.ROHF):
            return "ROHF"
        return "RHF"

    @staticmethod
    def reorder_molecular_orbitals_columns(
        mo_coeff: np.ndarray, column_order: list[int]
    ) -> np.ndarray:
        """Apply an MO column permutation ``i -> column_order.index`` analog to ``make_actives_contiguous`` steps."""
        m = np.asarray(mo_coeff, dtype=float)
        perm = list(column_order)
        if sorted(perm) != list(range(m.shape[1])):
            raise ValueError("column_order must be a permutation of range(n_molecular_orbitals).")
        return np.asarray(m[:, perm], dtype=float)

    def make_actives_contiguous_columns(
        self,
        mo_coeff: np.ndarray,
        active_molecular_orbital_indices: list[int],
        *,
        frozen_prefix_count: int = 0,
    ) -> tuple[np.ndarray, list[int]]:
        """Rotate MO columns toward ``[inactive… | contiguous actives … | inactive…]``.

        Returns the permuted coefficient matrix plus the permutation of **old** MO indices consumed.
        ``frozen_prefix_count`` optional leading core columns left untouched relative to inactive pool.
        """
        m = np.asarray(mo_coeff, dtype=float)
        nmo = int(m.shape[1])
        frozen_prefix_count = int(max(0, frozen_prefix_count))
        if frozen_prefix_count > nmo:
            raise ValueError("frozen_prefix_count exceeds MO dimension.")
        act = sorted({int(i) for i in active_molecular_orbital_indices})
        pool = list(range(nmo))
        inactive = [i for i in pool if i not in act]
        prefix = inactive[:frozen_prefix_count]
        rest_inactive = [i for i in inactive if i not in prefix]
        perm = prefix + act + rest_inactive
        if len(set(perm)) != nmo:
            raise ValueError("active indices overlap frozen prefix selections.")
        return self.reorder_molecular_orbitals_columns(m, perm), perm

    def get_ncas_nelec_couplet(
        self,
        *,
        resolved_reference: ClassicalMeanFieldReference | None = None,
    ) -> tuple[int, int]:
        """Return ``(n_active_spatial_orbitals, n_active_electrons)`` from YAML or resolved AVAS payload."""
        from qchem_stack.chem.active_space.pyscf_active_space_hooks import (
            RESOLVED_ACTIVE_SPACE_META_KEY,
        )

        if resolved_reference is not None:
            blk = resolved_reference.driver_meta.get(RESOLVED_ACTIVE_SPACE_META_KEY)
            if isinstance(blk, dict) and blk.get("n_active_orbitals") is not None:
                return int(blk["n_active_orbitals"]), int(blk["n_active_electrons"])  # type: ignore[index]
        if self.active_space is None:
            raise ValueError(
                "active_space unavailable; construct PySCFDriver.from_config(...) first."
            )
        return int(self.active_space.n_active_orbitals), int(self.active_space.n_active_electrons)

    def get_system_ao(
        self,
        rhf: PySCFRHFResult | None = None,
        *,
        run_hf: bool = True,
    ) -> PySCFAOSystem:
        """
        Return an AO-facing wrapper around the PySCF SCF object.

        This mirrors the InQuanto-PySCF ``get_system_ao`` design intent:
        keep AO data and the underlying SCF object available for fragment builders.
        """
        if self.chemistry_extended.pbc_cell_vectors_bohr is not None:
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

        # AO handle without a full SCF run (useful for fragment workflows that avoid global SCF).
        solv = self._integral_solver()
        mf = solv.build_molecular_mf_without_kernel()
        meta = dict(solv.idle_molecular_driver_meta())
        if self.chemistry_extended.solvent_model == "ddcosmo":
            meta.setdefault("solvent", "ddcosmo")
            meta.setdefault("ddcosmo_epsilon", float(self.chemistry_extended.ddcosmo_epsilon))
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
        """
        Build Löwdin-orthogonal AO integrals and 1-RDM for embedding workflows (DMET/FMO-style pre-stage).
        """
        if self.chemistry_extended.pbc_cell_vectors_bohr is not None:
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
    ) -> "RestrictedActiveSpaceQuantumProblem":  # noqa: UP037, F821
        """Open-stack analog to InQuanto ``get_system()`` for MO active-space restricted problems.

        Returns :class:`~qchem_stack.chem.molecular_problem.RestrictedActiveSpaceQuantumProblem`:
        :class:`~qchem_stack.chem.restricted_integral_operator.RestrictedActiveSpaceIntegralOperatorCompact`
        (PySCF-compact MO ERIs + pandas ``df`` helpers),
        OpenFermion :class:`~openfermion.InteractionOperator`, :class:`~qchem_stack.chem.fermion.FermionSpace`,
        Jordan–Wigner Hartree–Fock state vector, and :class:`~qchem_stack.chem.hamiltonian.QubitHamiltonian`.

        Use ``prefer_restricted_spatial_fermion_for_jordan_wigner=True`` with Jordan–Wigner to map via
        spatial-MO :class:`openfermion.FermionOperator` (avoids allocating a dense ``(2*ncas)^4`` spin ERI
        tensor for the JW step only). ``interaction_operator`` is still materialized from the compact pack for
        API parity. ``jordan_wigner_coeff_atol`` is incompatible with that spatial-fermion shortcut.

        When the driver was constructed via :meth:`from_config`, ``None`` for the JW optimizer kwargs means:
        inherit ``prefer_restricted_spatial_fermion_for_jordan_wigner`` and ``jordan_wigner_coeff_atol`` from
        the experiment ``active_space`` block.

        For AO-wrapped mean-field handles (FMO-style workflows), use :meth:`get_system_ao`.
        """
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
                bool(self.active_space.prefer_restricted_spatial_fermion_for_jordan_wigner)
                if self.active_space is not None
                else False
            )
        else:
            prefer_eff = prefer_restricted_spatial_fermion_for_jordan_wigner
        atol_eff = jordan_wigner_coeff_atol
        if atol_eff is None and self.active_space is not None:
            atol_eff = self.active_space.jordan_wigner_coeff_atol
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
        """
        Run a compact classical benchmark suite on the current mean-field reference.

        Returns a stable machine-readable payload with per-method status blocks:
        ``hf``, ``mp2``, ``ccsd``, ``casci``.
        """
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
        """
        PySCF :mod:`pyscf.pbc` mean field: ``RHF`` at Γ if ``pbc_kpoint_mesh`` is ``[1,1,1]``,
        else :class:`pyscf.pbc.scf.khf.KRHF` with ``cell.make_kpts``.

        Optional :class:`pyscf.solvent.ddCOSMO` is applied when ``solvent_model==ddcosmo`` (PySCF-dependent).
        """
        run = self._integral_solver().compute_mean_field(periodic=True)
        meta = dict(run.driver_meta)
        if self.chemistry_extended.solvent_model == "ddcosmo":
            meta.setdefault("solvent", "ddcosmo")
            meta.setdefault("ddcosmo_epsilon", float(self.chemistry_extended.ddcosmo_epsilon))
        from qchem_stack.chem.bridges.interchange import merge_canonical_classical_bridge_headers

        meta = merge_canonical_classical_bridge_headers(
            meta,
            upstream_software_tag="pyscf",
            periodic_boundary_condition=True,
        )
        return PySCFRHFResult(
            mf=run.mf,
            e_tot=run.e_tot,
            mo_energy=run.mo_energy,
            molecular_system=self.system,
            driver_meta=meta,
        )

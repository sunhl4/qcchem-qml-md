from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver
from qchem_stack.chem.system import MolecularSystem
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


@dataclass
class PySCFAOSystem:
    """AO-oriented handle that keeps the underlying PySCF SCF object accessible."""

    mf: Any
    molecular_system: MolecularSystem
    driver_meta: dict[str, Any] = field(default_factory=dict)
    has_run_hf: bool = True
    e_tot: float | None = None

    def ao_driver_summary_df(self) -> Any:
        """Notebook-friendly AO/system descriptor (cf. tutorials wrapping ``mf`` / ``mol``)."""
        import pandas as pd

        mol = self.mf.mol
        rows = [
            {"quantity": "nao_nr", "value": int(mol.nao_nr())},
            {"quantity": "nelectron", "value": int(mol.nelectron)},
            {"quantity": "spin", "value": int(mol.spin)},
            {"quantity": "basis_repr", "value": str(mol.basis)},
            {"quantity": "groupname", "value": getattr(mol, "groupname", None)},
            {
                "quantity": "integral_representation",
                "value": self.driver_meta.get("integral_representation"),
            },
            {"quantity": "ao_reference_kind", "value": self.driver_meta.get("ao_reference_kind")},
            {"quantity": "ao_run_hf", "value": self.driver_meta.get("ao_run_hf")},
        ]
        return pd.DataFrame(rows)


@dataclass
class PySCFLowdinSystem:
    """Löwdin-orthogonal AO representation for embedding-style workflows."""

    constant: float
    h1_spatial: np.ndarray
    h2_spatial: np.ndarray
    rdm1_spatial: np.ndarray
    molecular_system: MolecularSystem
    driver_meta: dict[str, Any] = field(default_factory=dict)


def active_space_casci_raw_blocks(
    rhf: PySCFRHFResult,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """CASCI MO integral blocks before OpenFermion reorder / dense restore.

    ``h2_spatial[p,q,r,s]`` is chemists' notation (pq|rs) over active spatial orbitals after dense restore.
    ``constant`` is PySCF CASCI ``energy_core`` from :meth:`pyscf.mcscf.CASCI.get_h1eff` (nuclear repulsion plus
    inactive-core contributions when ``ncore > 0``); it must not be summed again with ``energy_nuc``.

    ``h2eff`` from :meth:`pyscf.mcscf.CASCI.get_h2eff` may be **compact** (ndim ``!= 4``); callers should pass
    through :func:`pyscf.ao2mo.restore` before spatial reordering.
    """
    from pyscf import mcscf

    rhf = unwrap_pyscf_rhf_for_backend_operations(rhf)
    mf = rhf.mf
    meta = getattr(rhf, "driver_meta", None) or {}
    _ik = meta.get("pbc_active_space_kpoint_index")
    ik = int(_ik if _ik is not None else 0)
    mo_coeff = mf.mo_coeff
    if isinstance(mo_coeff, np.ndarray):
        mo = mo_coeff
    else:
        moc = list(mo_coeff)
        if ik >= len(moc):
            ik = 0
        mo = np.asarray(moc[ik], dtype=complex)
        if np.max(np.abs(mo.imag)) < 1e-10:
            mo = np.asarray(mo.real, dtype=float)
    n_mo = int(mo.shape[1])
    if n_active_orbitals > n_mo:
        raise ValueError("active orbitals exceed MO count at chosen k-point")
    cas = mcscf.CASCI(mf, n_active_orbitals, n_active_electrons)
    frozen_cfg = list(meta.get("active_space_frozen_orbitals") or [])
    if frozen_cfg:
        if any(i < 0 for i in frozen_cfg):
            raise ValueError("active_space_frozen_orbitals entries must be >= 0.")
        if any(i >= n_mo for i in frozen_cfg):
            raise ValueError(
                f"active_space_frozen_orbitals index out of bounds for n_mo={n_mo}: {frozen_cfg}"
            )
        cas.frozen = sorted(set(int(i) for i in frozen_cfg))
    h1, e_core = cas.get_h1eff(mo)
    h2 = cas.get_h2eff(mo)
    h1a = np.asarray(h1, dtype=complex)
    h2a = np.asarray(h2, dtype=complex)
    for label, arr in (("h1", h1a), ("h2", h2a)):
        if np.max(np.abs(arr.imag)) > 1e-7:
            raise ValueError(
                f"Active space {label} has non-trivial imaginary part; use Gamma (mesh [1,1,1]) or a real k-point."
            )
    # ``e_core`` from ``CASCI.get_h1eff`` / ``h1e_for_cas`` already starts at
    # ``energy_nuc()`` and adds inactive-orbital contributions when ``ncore > 0``;
    # do not add ``mol.energy_nuc()`` again (would double-count nuclear repulsion).
    constant = float(e_core)
    h1_out = np.asarray(h1a.real, dtype=float)
    h2_real = np.asarray(h2a.real, dtype=float)
    # PySCF 2.x ``get_h2eff`` often returns chemists' ERIs in compact 2D form
    # (``n * (n + 1) // 2`` square); OpenFermion expects full ``(n, n, n, n)``.
    n_act = int(n_active_orbitals)
    if h2_real.ndim == 4:
        h2_out = h2_real
    elif h2_real.ndim == 2:
        from pyscf import ao2mo

        h2_out = np.asarray(ao2mo.restore(1, h2_real, n_act), dtype=float)
    else:
        raise ValueError(f"unexpected active-space h2 shape {h2_real.shape} (ndim={h2_real.ndim})")
    return constant, h1_out, h2_out


def active_space_integrals(
    rhf: PySCFRHFResult,
    n_active_orbitals: int,
    n_active_electrons: int,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return (constant, h1_spatial, h2_spatial) for OpenFermion ``InteractionOperator``.

    ``h2_spatial`` is the active-space MO ERI tensor after **Tangelo/OpenFermion reordering**
    (:func:`~qchem_stack.chem.integral_convention.spatial_mo_eri_pyscf_to_openfermion_mo_ordering`)
    on PySCF ``get_h2eff`` / ``ao2mo.restore`` output. Callers then use
    ``spinorb_from_spatial`` and ``InteractionOperator(..., 0.5 * h2_spin_orb)`` as in
    SandboxAQ Tangelo's ``SecondQuantizedMolecule._get_fermionic_hamiltonian``.

    The constant is PySCF ``get_h1eff``'s ``energy_core`` (nuclear repulsion plus
    frozen-core electronic energy when ``ncore>0``); do not add ``energy_nuc`` again.
    """
    from pyscf import ao2mo

    constant, h1_real, h2_store = active_space_casci_raw_blocks(
        rhf, n_active_orbitals, n_active_electrons
    )
    if h2_store.ndim != 4:
        h2a = np.asarray(
            ao2mo.restore(1, np.asarray(h2_store, dtype=float), int(n_active_orbitals)),
            dtype=float,
        )
    else:
        h2a = np.asarray(h2_store, dtype=float)
    from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering

    h2_spatial = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(h2a)
    return constant, h1_real, h2_spatial


class PySCFDriver:
    """Minimal PySCF RHF/ROHF/UHF driver behind extension boundary."""

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

    @staticmethod
    def _spatial_one_body_to_fermion_operator(h1_spatial: np.ndarray) -> Any:
        from openfermion import FermionOperator

        h1 = np.asarray(h1_spatial, dtype=float)
        n = int(h1.shape[0])
        out = FermionOperator()
        for p in range(n):
            for q in range(n):
                c = float(h1[p, q])
                if abs(c) < 1e-14:
                    continue
                out += FermionOperator(((2 * p, 1), (2 * q, 0)), c)
                out += FermionOperator(((2 * p + 1, 1), (2 * q + 1, 0)), c)
        return out

    @staticmethod
    def _transform_ao_to_mo(ao_mat: np.ndarray, mo_coeff: np.ndarray) -> np.ndarray:
        c = np.asarray(mo_coeff, dtype=float)
        a = np.asarray(ao_mat, dtype=float)
        return np.asarray(c.T @ a @ c, dtype=float)

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
        mf = pr.mf
        mol = mf.mol
        mo = np.asarray(mf.mo_coeff, dtype=float)
        if oper == "kin":
            h = mol.intor_symmetric("int1e_kin")
            return self._spatial_one_body_to_fermion_operator(self._transform_ao_to_mo(h, mo))
        if oper == "nuc":
            h = mol.intor_symmetric("int1e_nuc")
            return self._spatial_one_body_to_fermion_operator(self._transform_ao_to_mo(h, mo))
        if oper == "hcore":
            h = mf.get_hcore()
            return self._spatial_one_body_to_fermion_operator(self._transform_ao_to_mo(h, mo))
        if oper == "ovlp":
            h = mf.get_ovlp()
            return self._spatial_one_body_to_fermion_operator(self._transform_ao_to_mo(h, mo))
        with mol.with_common_origin(tuple(map(float, origin))):
            if oper in ("r", "dm"):
                mats = np.asarray(mol.intor("int1e_r"), dtype=float).reshape(
                    3, mo.shape[0], mo.shape[0]
                )
                if oper == "dm":
                    mats = -mats
                return [
                    self._spatial_one_body_to_fermion_operator(self._transform_ao_to_mo(m, mo))
                    for m in mats
                ]
            if oper == "rr":
                mats = np.asarray(mol.intor("int1e_rr"), dtype=float).reshape(
                    9, mo.shape[0], mo.shape[0]
                )
                return [
                    self._spatial_one_body_to_fermion_operator(self._transform_ao_to_mo(m, mo))
                    for m in mats
                ]
        raise ValueError(f"Unsupported one-electron operator key: {oper!r}")

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
        from openfermion import bravyi_kitaev, jordan_wigner, symmetry_conserving_bravyi_kitaev

        fop = self.compute_one_electron_operator_fermion(oper, origin=origin, rhf=rhf)

        def _map_one(op: Any) -> Any:
            if fermion_qubit_mapping == "jordan_wigner":
                return jordan_wigner(op)
            if fermion_qubit_mapping == "bravyi_kitaev":
                return bravyi_kitaev(op)
            n_spin_orbitals = int(
                2 * np.asarray((rhf.mf if rhf else self.run_rhf().mf).mo_coeff).shape[1]
            )
            if n_electrons is None:
                raise ValueError(
                    "compute_one_electron_operator_pauli(..., fermion_qubit_mapping='symmetry_conserving_bravyi_kitaev') "
                    "requires n_electrons."
                )
            return symmetry_conserving_bravyi_kitaev(
                op, n_spin_orbitals=n_spin_orbitals, n_electrons=int(n_electrons)
            )

        if isinstance(fop, list):
            return [_map_one(x) for x in fop]
        return _map_one(fop)

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
        mf = rhf.mf
        mol = mf.mol
        s = np.asarray(mf.get_ovlp(), dtype=float)
        # C_lowdin^T S C_lowdin = I
        evals, evecs = np.linalg.eigh(s)
        if np.min(evals) <= 1e-12:
            raise ValueError(
                "AO overlap matrix is near singular; cannot build stable Löwdin basis."
            )
        c_low = np.asarray(evecs @ np.diag(evals**-0.5) @ evecs.T, dtype=float)
        hcore = np.asarray(mf.get_hcore(), dtype=float)
        h1_low = np.einsum("pi,pq,qj->ij", c_low, hcore, c_low, optimize=True)
        n_ao = int(hcore.shape[0])
        eri_ao = np.asarray(mol.intor("int2e", aosym="s1"), dtype=float).reshape(
            n_ao, n_ao, n_ao, n_ao
        )
        h2_low = np.einsum(
            "pa,qb,rc,sd,pqrs->abcd", c_low, c_low, c_low, c_low, eri_ao, optimize=True
        )
        dm_ao_raw = mf.make_rdm1()
        if isinstance(dm_ao_raw, (tuple, list)):
            dm_ao = np.asarray(dm_ao_raw[0], dtype=float) + np.asarray(dm_ao_raw[1], dtype=float)
        else:
            dm_ao = np.asarray(dm_ao_raw, dtype=float)
        c_inv = np.linalg.inv(c_low)
        dm_low = np.asarray(c_inv @ dm_ao @ c_inv.T, dtype=float)
        meta = dict(rhf.driver_meta)
        meta["integral_representation"] = "lowdin_orth_ao"
        meta["lowdin_basis_transform"] = "s^-1/2"
        return PySCFLowdinSystem(
            constant=float(mol.energy_nuc()),
            h1_spatial=np.asarray(h1_low, dtype=float),
            h2_spatial=np.asarray(h2_low, dtype=float),
            rdm1_spatial=np.asarray(dm_low, dtype=float),
            molecular_system=self.system,
            driver_meta=meta,
        )

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

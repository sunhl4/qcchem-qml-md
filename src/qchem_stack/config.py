from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator, model_validator

from qchem_stack.exceptions import ConfigurationError

# CODATA-compatible: Bohr radius in ångströms (chemistry YAML often uses Å).
_BOHR_RADIUS_IN_ANGSTROM = 0.529177210903
ANGSTROM_TO_BOHR = 1.0 / _BOHR_RADIUS_IN_ANGSTROM


class MoleculeSpec(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    symbols: list[str]
    coordinates: list[list[float]] | None = Field(
        default=None,
        validation_alias=AliasChoices("coordinates", "coordinates_bohr"),
        description=(
            "Atomic Cartesian coordinates in ``coordinate_unit``. "
            "YAML may use legacy key ``coordinates_bohr`` (values interpreted as Bohr unless "
            "``coordinate_unit`` is set explicitly)."
        ),
    )
    zmatrix: str | None = Field(
        default=None,
        validation_alias=AliasChoices("zmatrix", "z_matrix"),
        description=(
            "Optional Z-matrix molecular geometry text. When provided (and ``coordinates`` is omitted), "
            "it is converted to Cartesian Bohr coordinates internally."
        ),
    )
    coordinate_unit: Literal["angstrom", "bohr"] = Field(
        default="angstrom",
        description=(
            "Length unit for ``coordinates``. Defaults to **ångström** for the canonical ``coordinates`` key; "
            "if the legacy alias ``coordinates_bohr`` is used and this field is omitted, it defaults to **bohr**."
        ),
    )
    charge: int = 0
    multiplicity: int = 1
    basis: str = "sto-3g"
    ecp: str | dict[str, str] | None = None

    @model_validator(mode="before")
    @classmethod
    def _legacy_coordinates_bohr_unit(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)
        if "coordinates_bohr" in out and "coordinate_unit" not in out:
            out["coordinate_unit"] = "bohr"
        return out

    @model_validator(mode="after")
    def _validate_geometry_source(self) -> MoleculeSpec:
        if self.coordinates is None and not (self.zmatrix and self.zmatrix.strip()):
            raise ValueError("molecule requires either coordinates/coordinates_bohr or a non-empty zmatrix.")
        if self.coordinates is not None and self.zmatrix:
            raise ValueError("molecule.coordinates and molecule.zmatrix are mutually exclusive.")
        return self

    def coordinates_in_bohr(self):
        """Positions as a float ndarray in Bohr (PySCF ``gto.M`` internal convention)."""
        import numpy as np

        if self.coordinates is not None:
            arr = np.asarray(self.coordinates, dtype=float)
            if self.coordinate_unit == "angstrom":
                return arr * ANGSTROM_TO_BOHR
            return arr.copy()
        try:
            from pyscf import gto
        except ImportError as exc:
            raise ConfigurationError(
                "molecule.zmatrix requires PySCF to convert internal coordinates to Cartesian Bohr."
            ) from exc
        mol = gto.M(
            atom=str(self.zmatrix),
            basis=str(self.basis),
            charge=int(self.charge),
            spin=int(self.multiplicity) - 1,
            unit="Angstrom",
            ecp=self.ecp,
            verbose=0,
        )
        return np.asarray(mol.atom_coords(unit="Bohr"), dtype=float)


class SCFSpec(BaseModel):
    """Classical Hartree–Fock driver selection (Hamiltonian build path is PySCF-first today)."""

    driver: Literal["pyscf", "psi4"] = "pyscf"
    method: Literal["RHF", "ROHF", "UHF"] = "RHF"
    max_cycle: int | None = Field(
        default=None,
        ge=1,
        le=512,
        description="Optional PySCF ``mf.max_cycle`` override (open-shell / transition-metal SCF).",
    )
    chkfile: str | None = Field(
        default=None,
        description="Optional PySCF checkpoint path (``mf.chkfile``).",
    )
    init_guess: str | None = Field(
        default=None,
        description=(
            "Optional PySCF ``mf.init_guess`` token (e.g. ``minao``, ``atom``, ``huckel``, ``chkfile``)."
        ),
    )
    level_shift: float | None = Field(
        default=None,
        description="Optional mean-field ``level_shift`` when supported by PySCF SCF objects.",
    )
    use_newton: bool = Field(
        default=False,
        description="If True and method is RHF/ROHF, use ``scf.RHF(...).newton()`` pipeline when available.",
    )
    diis_space_dimension: int | None = Field(
        default=None,
        ge=2,
        description="Optional ``mf.diis_space`` dimension override (PySCF-dependent).",
    )
    density_fit: bool = Field(
        default=False,
        description="Enable density-fitting / RI SCF when supported by the selected backend.",
    )
    density_fit_auxbasis: str | None = Field(
        default=None,
        description="Optional auxiliary basis for density-fitting (PySCF ``mf.density_fit(auxbasis=...)``).",
    )

    @model_validator(mode="after")
    def _density_fit_auxbasis_consistency(self) -> SCFSpec:
        if self.density_fit_auxbasis and not self.density_fit:
            raise ValueError("scf.density_fit_auxbasis requires scf.density_fit=true.")
        return self


class ActiveSpaceSpec(BaseModel):
    strategy: Literal["manual", "cas", "avas_stub", "avas"] = "cas"
    """
    Active-space entry mode:

    - ``cas``: canonical CAS notation via ``ncas/nelecas`` (or legacy ``n_active_*`` aliases).
    - ``manual``: explicit active-space sizes plus optional ``frozen_orbitals`` bookkeeping.
    - ``avas_stub``: **hook-only** — same **CAS** sizing as ``cas`` (``ncas`` / ``nelecas``); no AO threshold projection.
      Honesty metadata is written by
      :func:`~qchem_stack.chem.active_space.mean_field_meta.apply_active_space_strategy_to_mean_field_meta`
      (e.g. ``avas_partial_stub``, ``avas_atomic_projection_executed``, ``avas_stub_semantics``).
      Does **not** build InQuanto/PySCF-style ``frozen=avas.frozenf`` from atomic valence weights.
    - ``avas``: **PySCF path** — run :class:`pyscf.mcscf.avas.AVAS` threshold projection using
      ``chemistry_extended.avas_ao_labels`` and related AVAS knobs, rotate ``mf.mo_coeff``, then
      patch YAML-sized ``ncas`` / ``nelecas`` via ``driver_meta.qchem_active_space_resolution_v1``
      inside the pipeline (repro parity with AVAS-derived active dimensions).
    """
    n_active_orbitals: int | None = None
    n_active_electrons: int | None = None
    ncas: int | None = None
    nelecas: int | None = None
    frozen_orbitals: list[int] = Field(default_factory=list)
    fermion_qubit_mapping: Literal[
        "jordan_wigner",
        "bravyi_kitaev",
        "symmetry_conserving_bravyi_kitaev",
    ] = "jordan_wigner"
    """OpenFermion transform from :class:`openfermion.InteractionOperator` to :class:`openfermion.QubitOperator`."""
    prefer_restricted_spatial_fermion_for_jordan_wigner: bool = Field(
        default=False,
        description=(
            "Jordan–Wigner only: build :class:`openfermion.FermionOperator` from spatial MO integrals then JW, "
            "avoiding a dense (2×ncas)⁴ spin ERI tensor for that mapping step (see "
            ":func:`~qchem_stack.chem.hamiltonian.molecular_hamiltonian_from_classical_reference`)."
        ),
    )
    jordan_wigner_coeff_atol: float | None = Field(
        default=None,
        description=(
            "Optional positive cutoff on the InteractionOperator JW path (skip negligible coefficient shells). "
            "Must be omitted when prefer_restricted_spatial_fermion_for_jordan_wigner is True."
        ),
    )

    @field_validator("frozen_orbitals")
    @classmethod
    def _validate_frozen_orbitals(cls, v: list[int]) -> list[int]:
        if any(i < 0 for i in v):
            raise ValueError("active_space.frozen_orbitals entries must be >= 0.")
        if len(set(v)) != len(v):
            raise ValueError("active_space.frozen_orbitals must not contain duplicates.")
        return list(v)

    @model_validator(mode="after")
    def _normalize_active_space_entry(self) -> ActiveSpaceSpec:
        if self.strategy in ("cas", "avas_stub", "avas"):
            if self.ncas is not None and self.n_active_orbitals is not None and int(self.ncas) != int(
                self.n_active_orbitals
            ):
                raise ValueError("active_space.ncas and n_active_orbitals disagree for strategy='cas'.")
            if self.nelecas is not None and self.n_active_electrons is not None and int(self.nelecas) != int(
                self.n_active_electrons
            ):
                raise ValueError("active_space.nelecas and n_active_electrons disagree for strategy='cas'.")
            ncas = self.ncas if self.ncas is not None else self.n_active_orbitals
            nelecas = self.nelecas if self.nelecas is not None else self.n_active_electrons
            if ncas is None or nelecas is None:
                raise ValueError(
                    "active_space.strategy in {'cas','avas_stub','avas'} requires ncas/nelecas "
                    "(or legacy n_active_orbitals/n_active_electrons)."
                )
            if int(ncas) < 1 or int(nelecas) < 1:
                raise ValueError("active_space ncas/nelecas must both be >= 1.")
            self.ncas = int(ncas)
            self.nelecas = int(nelecas)
            self.n_active_orbitals = int(ncas)
            self.n_active_electrons = int(nelecas)
            return self

        # manual strategy
        if self.n_active_orbitals is None or self.n_active_electrons is None:
            raise ValueError(
                "active_space.strategy='manual' requires n_active_orbitals and n_active_electrons."
            )
        if int(self.n_active_orbitals) < 1 or int(self.n_active_electrons) < 1:
            raise ValueError("active_space n_active_orbitals/n_active_electrons must both be >= 1.")
        if self.ncas is not None and int(self.ncas) != int(self.n_active_orbitals):
            raise ValueError("active_space.ncas must equal n_active_orbitals when strategy='manual'.")
        if self.nelecas is not None and int(self.nelecas) != int(self.n_active_electrons):
            raise ValueError("active_space.nelecas must equal n_active_electrons when strategy='manual'.")
        self.n_active_orbitals = int(self.n_active_orbitals)
        self.n_active_electrons = int(self.n_active_electrons)
        self.ncas = int(self.n_active_orbitals)
        self.nelecas = int(self.n_active_electrons)
        return self

    @model_validator(mode="after")
    def _jw_optimizer_flags_consistent(self) -> ActiveSpaceSpec:
        if self.prefer_restricted_spatial_fermion_for_jordan_wigner:
            if self.fermion_qubit_mapping != "jordan_wigner":
                raise ValueError(
                    "active_space.prefer_restricted_spatial_fermion_for_jordan_wigner requires "
                    "active_space.fermion_qubit_mapping='jordan_wigner'."
                )
            if self.jordan_wigner_coeff_atol is not None:
                raise ValueError(
                    "active_space.jordan_wigner_coeff_atol cannot be set when "
                    "prefer_restricted_spatial_fermion_for_jordan_wigner is True."
                )
        if self.jordan_wigner_coeff_atol is not None and float(self.jordan_wigner_coeff_atol) <= 0:
            raise ValueError("active_space.jordan_wigner_coeff_atol must be positive when set.")
        return self


class BackendSpecConfig(BaseModel):
    name: str = "statevector_sim"
    provider: Literal["statevector", "qiskit", "ionstack"] = "statevector"
    shots_per_circuit: int = 2048
    target_energy_stderr: float | None = None
    qiskit_mode: Literal["statevector", "estimator"] = "statevector"
    ionstack_endpoint: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class MitigationSpec(BaseModel):
    """Aligned with InQuanto docs: classify mitigation by **orchestration** (sync graph vs async batch)."""

    execution_class: Literal["unspecified", "sync_graph", "async_batch", "shot_postselect"] = "unspecified"
    """``sync_graph``: Qermit-style DAG; ``async_batch``: launch/retrieve-friendly; ``shot_postselect``: PMSV-style."""
    pmsv_enabled: bool = False
    zne_enabled: bool = False
    zne_mode: Literal["scalar_stub", "circuit_scale_fold"] = "scalar_stub"
    """``scalar_stub``: scale energies via :func:`~qchem_stack.mitigation.zne.zne_scale_energy`; ``circuit_scale_fold``: exact HEA-depth amplification per scale (statevector path only; sampled/Qiskit shots fall back to stub)."""
    zne_scales: list[float] = Field(
        default_factory=lambda: [1.0, 1.5, 2.0],
    )
    """Noise-amplified curve abscissas for the open-stack ZNE stub (``zne_scale_energy``) and :mod:`qermit_runtime` execution."""
    pmsv_stabilizers: list[str] = Field(default_factory=list)
    """Symbolic labels (e.g. ``Z0 Z1``) for Methods; toy filter uses :attr:`pmsv_retention_rate` only unless extended."""
    pmsv_retention_rate: float = 1.0
    """Post-selection retention in :math:`(0,1]`; scatters stderr when ``< 1`` (see PMSV stub). Defaults to 1 (no PMSV shot loss)."""
    pmsv_report_extension: str = "default"
    """Hook name for :func:`qchem_stack.mitigation.pmsv.finalize_pmsv_report` (extensible PMSV metadata)."""
    pmsv_extra: dict[str, Any] = Field(default_factory=dict)
    """Opaque key-value pass-through into ``protocol_counts['pmsv_report']`` (plugin / lab metadata)."""
    spam_calibration_enabled: bool = False
    """When true, include a readout-correction stub node in ``mitigation_graph_report`` (before PMSV/ZNE)."""
    pec_literature_stub_enabled: bool = False
    """
    When true, emit ``mitigation_pec_literature_stub_v1`` under ``repro.parity_snapshot`` (P2-W4).

    Literature-facing placeholder for PEC / quasi-probability narratives — **not** Qermit MitRes and not a
    calibrated error cancellation executor.
    """
    classical_shadows_stub_enabled: bool = False
    """
    Insert a ``classical_shadows_expectation_stub`` DAG node + runtime trace (identity on scalar energy).

    Open-stack analog to randomized-measurement narratives in toolboxes such as Tangelo — **no** device
    shadows sampling is performed here.
    """
    classical_shadows_budget_pairs: int = Field(default=256, ge=1, le=10_000_000)
    """Opaque hint integer for Methods export only (not consumed by numeric kernels in this stub)."""


class CompilerSpec(BaseModel):
    """Pass bundles analogous to InQuanto ``preoptimize_passes`` / ``compiler_passes`` knobs."""

    optimization_level: int = 1
    native_twoq: str = "CX"
    preoptimize_passes: list[str] = Field(default_factory=list)
    """Ansatz- or chemistry-adjacent logical passes (see :mod:`qchem_stack.backends.compile_passes`)."""
    compiler_passes: list[str] = Field(default_factory=list)
    """Target-backend passes applied after ``preoptimize_passes``."""


class ChemistryExtendedSpec(BaseModel):
    """Extended driver surface (InQuanto-adjacent names; PySCF where implemented)."""

    solvent_model: Literal["none", "ddcosmo"] = "none"
    """``ddcosmo``: wrap SCF with :class:`pyscf.solvent.ddCOSMO` before ``kernel``."""
    ddcosmo_epsilon: float = 78.3553
    """Solvent dielectric (default water) for ddCOSMO."""
    pbc_cell_vectors_bohr: list[list[float]] | None = None
    """3×3 lattice row vectors in Bohr for :mod:`pyscf.pbc` (``PySCFDriver.run_pbc_rhf``)."""
    pbc_kpoint_mesh: list[int] = Field(default_factory=lambda: [1, 1, 1])
    """Monkhorst–Pack mesh ``[nx,ny,nz]``; all ``1`` → Γ-only :class:`pyscf.pbc.scf.hf.RHF`, else :class:`pyscf.pbc.scf.khf.KRHF` with that mesh."""
    pbc_active_space_kpoint_index: int = 0
    """Which k-point in ``KRHF`` MO list to use for CASCI / active-space integrals (Γ is usually index ``0`` in PySCF ordering)."""
    casscf_orbital_optimization_audit: bool = False
    """
    Molecular RHF branch only: run PySCF :class:`pyscf.mcscf.CASSCF` for the resolved active-space
    electron/orbital counts (after optional AVAS) and record ``casscf_orbital_audit_v1`` in ``driver_meta``
    unless ``casscf_orbital_optimization_for_integrals`` alone is enabled (audit can be bundled with the same
    CASSCF call when either flag is true).
    """

    casscf_orbital_optimization_for_integrals: bool = False
    """
    When ``True`` (PySCF molecular RHF), rotate ``mf.mo_coeff`` using the optimized CASSCF orbitals **before**
    CASCI-style active extracts used for ``CanonicalActiveSpaceIntegralPack`` / JW Hamiltonians.
    Pairs naturally after ``active_space.strategy=avas`` while still respecting solver capability gates.

    Implemented as a shared single ``CASSCF`` kernel with ``casscf_orbital_optimization_audit`` so enabling
    both does **not** run CASSCF twice.
    """
    classical_benchmark_enabled: bool = False
    """
    When ``True``, pipeline attaches ``classical_benchmarks`` via
    :func:`qchem_stack.chem.classical_benchmarks.run_classical_post_hf_benchmarks`
    (HF/MP2/CCSD/CASCI status blocks; schema ``qchem_classical_post_hf_benchmarks_v1``).
    """
    classical_benchmark_backend: Literal["auto", "stub", "pyscf", "psi4"] = "auto"
    """
    Which chemistry backend executes post-HF benchmarks.

    ``auto``: use PySCF benchmarks when the mean-field reference reports ``upstream_classical_software_tag=pyscf``;
    otherwise attach a stub payload. ``pyscf`` / ``psi4`` force that registry path (``psi4`` is placeholder-only today).
    """
    rdm_correction_method: Literal["none", "stub_nevpt2", "stub_ac0", "pyscf_nevpt2_casci"] = "none"
    """
    Optional post-SCF RDM correction hook (Phase C / Phase 3).
    ``stub_*``: machine-readable reports only (zero numerical correction).
    ``pyscf_nevpt2_casci``: PySCF ``mrpt.NEVPT`` on a CASCI reference (open stack — not InQuanto L0).
    """
    avas_ao_labels: list[str] = Field(default_factory=list)
    """
    Atomic-orbital label strings interpreted by PySCF :class:`~pyscf.mcscf.avas.AVAS` **when**
    ``active_space.strategy='avas'`` (required non-empty combination — validated on :class:`ExperimentConfig`).

    When non-empty **and strategy is not** ``avas``: copied to ``driver_meta["avas_ao_labels_requested"]`` and
    ``driver_meta["avas_ao_labels_logging_only"]=true`` without changing orbitals / integrals.

    Stub intent without projection remains ``strategy=avas_stub``.
    """

    avas_threshold: float = Field(default=0.2, gt=0.0, le=1.0)
    """AVAS orbital selection threshold forwarded to PySCF."""
    avas_minao: str = Field(default="minao", min_length=1)
    """Reference minimal basis forwarded to AVAS."""
    avas_with_iao: bool = False
    avas_openshell_option: int = Field(default=2, ge=0, le=10)
    """PySCF ``avas.AVAS`` openshell option (consult PySCF docs for semantics)."""
    avas_canonicalize: bool = True
    avas_ncore: int = Field(default=0, ge=0, le=512)
    """Frozen core orbital count forwarded to AVAS."""
    pyscf_symmetry: bool | str = False
    """
    Forwarded to PySCF ``gto.M(..., symmetry=...)`` on the molecular branch (non-PBC).

    ``True`` enables automatic subgroup detection; a non-empty **string** selects an explicit subgroup label
    understood by your PySCF build.

    This can reduce **classical** integral / SCF cost when symmetry applies. The bridge to OpenFermion for the
    quantum stage still materializes **dense** active-space tensors — there is **no** drop-in equivalent to
    InQuanto ``ChemistryRestrictedIntegralOperatorCompact`` in this repository yet.
    """
    mo_coeff_transform_hook: str = ""
    """
    Optional post-SCF MO transform hook name.

    Built-ins:
    - ``reverse_mo_columns``: deterministic column reversal for smoke/tests.
    - ``identity``: explicit no-op.

    Custom hooks may be provided as ``python_module:function_name`` and must return an array with the
    same shape as ``mf.mo_coeff``.
    """
    mo_coeff_transform_kwargs: dict[str, Any] = Field(default_factory=dict)
    """Opaque kwargs passed to the selected MO transform hook."""

    @model_validator(mode="after")
    def _validate_pbc_cell_matrix(self) -> ChemistryExtendedSpec:
        pbc = self.pbc_cell_vectors_bohr
        if len(self.pbc_kpoint_mesh) != 3 or any(n < 1 for n in self.pbc_kpoint_mesh):
            raise ValueError("chemistry_extended.pbc_kpoint_mesh must be three integers >= 1.")
        if pbc is None:
            return self
        if len(pbc) != 3 or any(len(row) != 3 for row in pbc):
            raise ValueError("chemistry_extended.pbc_cell_vectors_bohr must be a 3×3 matrix (Bohr).")
        import numpy as np

        a = np.asarray(pbc, dtype=float)
        if abs(float(np.linalg.det(a))) < 1e-12:
            raise ValueError("chemistry_extended.pbc_cell_vectors_bohr must be non-singular.")
        if self.pbc_active_space_kpoint_index < 0:
            raise ValueError("chemistry_extended.pbc_active_space_kpoint_index must be >= 0.")
        return self


class NexusAnalogSpec(BaseModel):
    """Local project + HQC **unit** ledger (no Nexus API, no real billing)."""

    enabled: bool = False
    project_label: str = "default"
    unit_per_circuit: float = 1.0
    unit_per_shot: float = 1e-4
    unit_per_depth: float = 1e-3


class NexusCloudSpec(BaseModel):
    """
    Optional real **Nexus/Quantinuum cloud** job adapter (opt-in, no secrets in YAML).

    Use ``NEXUS_API_KEY`` (or :attr:`api_key_env`) in the process environment; the open stack
    only ships a typed client + health/submit shims, not a vendor contract.
    """

    mode: Literal["off", "http", "mock"] = "off"
    base_url: str = ""
    """HTTPS API root (e.g. ``https://nexus.../v1``) — use only in ``http`` mode."""
    api_key_env: str = "NEXUS_API_KEY"
    project_slug: str = ""
    timeout_s: float = 30.0


class ParityIntegrationsSpec(BaseModel):
    """
    **Open-stack parity extensions** merged into ``repro.parity_snapshot``.

    Fills reproducibility JSON where vendor defaults are closed: we record *designed* public-contract
    analogs (TKET-shaped compile probe, UCCSD counts, DMET orchestration ledger, qnexus import health,
    Qermit-field mapping, TN strategy map). This is **L1 auditability**, not L0 binary parity with
    InQuanto wheels.
    """

    enabled: bool = True
    qnexus_probe: bool = True
    """``pip install qnexus`` import / version probe (no API calls)."""
    open_qermit_reference: bool = True
    """Static capability matrix vs :mod:`qchem_stack.mitigation.qermit_analog` / ``qermit_runtime``."""
    tensornet_closure_reference: bool = True
    """Strategy map pointing at :mod:`qchem_stack.tensornet.cutensornet_protocol_stub`."""
    uccsd_excitation_reference: bool = True
    """
    Closed-shell **spin-orbital** UCCSD excitation counts from active space
    (:math:`n_{so}=2 n_{active}^{spatial}`, :math:`n_e = n^{active}_{e}`).
    """
    tket_first_circuit_stats: bool = True
    """After Pauli protocol compile, run :func:`~qchem_stack.integrations.tket_fullchain.circuit_ir_to_tket_stats_or_none` on the first compiled ``CircuitIR``."""
    dmet_stub_one_shot_ledger: bool = True
    """When ``embedding.mode`` is ``dmet``, append ``OneShotEmbeddingDriver`` stub run for Methods traceability."""
    gap_closure_reference_bundle: bool = True
    """
    Attach ``open_gap_closure_reference`` (UCC/TKET/Nexus/Qermit/TN/L3/driver matrix) to
    ``parity_snapshot`` — **open engineered references**, not vendor L0 parity.
    """
    include_computables_rich_in_repro: bool = False
    """
    When ``True``, ``repro.workflow_preview_v1`` matches ``POST /v1/meta/workflow-preview`` with
    ``include_computables_rich=True`` (adds ``computables_rich`` / ``computables_rich_v1``).
    Default ``False`` keeps slimmer ``repro``; enable for strict L1 preview↔repro parity tests.
    """

    resource_estimation_preview: bool = False
    """
    When ``True``, ``export_parity_criteria_table`` may emit ``resource_estimation_preview_v1``
    (P2-W1 shallow Methods/resource narrative; no cloud pricing).
    """


class MdMlExportSpec(BaseModel):
    """Optional snapshot of :mod:`~qchem_stack.md_bridge` training schema onto ``repro``."""

    attach_single_frame_to_repro: bool = False
    """When ``True``, attach ``repro.qmef_ml_attachment_v1`` after the pipeline completes."""
    energy_reference: Literal["variational", "scf", "pauli_protocol"] = "variational"
    """
    Primary-frame total energy in Hartree: post-VQE ``energy_after_variational``, mean-field ``scf_energy``, or
    ``energy_pauli_protocol`` (requires ``quantum.use_pauli_protocol: true`` and a completed Pauli stage).
    Extra trajectory frames use nested pipeline energies only when ``trajectory_theory_level: full_pipeline``;
    HF-only extras always record mean-field ``e_tot``.
    """
    include_hf_nuclear_gradient: bool = False
    """
    Attempt PySCF analytic HF forces (:math:`-\\partial E/\\partial R`) in Hartree/Bohr for molecular clusters.
    Ignored on periodic / PBC drivers or when gradients raise.
    """
    extra_coordinates_bohr: list[list[list[float]]] = Field(default_factory=list)
    """
    Additional nuclear geometries (each ``n_atom × 3`` Bohr, same atom order as ``molecule.symbols``).

    Evaluated according to ``trajectory_theory_level`` after the primary pipeline finishes.
    """
    trajectory_theory_level: Literal["hf_scf", "full_pipeline"] = "hf_scf"
    """
    ``hf_scf``: PySCF mean-field energy (+ optional HF gradient) per extra geometry only.

    ``full_pipeline``: nested :func:`~qchem_stack.orchestration.pipeline.run_pipeline_sync` per geometry
    (QMEF attachment disabled on nested runs to avoid recursion).
    """


class EmbeddingSpec(BaseModel):
    """Falsifiability fields for DMET / projection workflows (chemistry pre-stage)."""

    mode: Literal["none", "dmet", "projection", "plugin"] = "none"
    embedding_input_representation: Literal["mo", "ao", "lowdin_orth_ao"] = "mo"
    """
    Pre-embedding chemistry representation preference (Phase B):
    ``mo`` (default), ``ao`` (SCF object wrapper), or ``lowdin_orth_ao`` (localized orthogonal AO tensors).
    """
    n_scf_cycles_embedding: int | None = None
    """How many self-consistent embedding sweeps; ``None`` if not used."""
    classical_reference_method: str | None = None
    """E.g. ``MP2``, ``CASSCF``, ``DLPNO-CC`` — documentation / parity only in this open stack."""
    projection_low_level: str = "HF"
    """Low-level reference for ``mode=='projection'`` (L1 trace; no PySCF projection driver yet)."""
    projection_high_level: str = "CAS"
    """High-level correlation label for projection trace (documentation-only until a driver is wired)."""
    projection_threshold: float = Field(default=1e-8, gt=0)
    """Numerical threshold recorded for Methods when ``mode=='projection'``."""
    projection_quantum_hamiltonian: Literal["global_active_space", "fragment_mulliken_mo"] = (
        "global_active_space"
    )
    """
    ``global_active_space`` (default): variational ``QubitHamiltonian`` from global
    :class:`ActiveSpaceSpec` (legacy L1 trace + projection metadata only).

    ``fragment_mulliken_mo``: build active orbitals by **Mulliken fragment weights** on
    ``projection_fragment_atom_indices``, then CASCI-core integrals + JW — see
    :mod:`qchem_stack.chem.embedding.projection_hamiltonian`.
    """
    projection_fragment_atom_indices: list[int] = Field(default_factory=list)
    """Zero-based atom indices for ``projection_quantum_hamiltonian=='fragment_mulliken_mo'`` (required when set)."""
    fragment_labels: list[str] = Field(default_factory=list)
    """Fragment ids when ``mode==dmet``; empty when ``none``."""
    dmet_hamiltonian_source: Literal[
        "parity_stub", "whole_active_system", "schmidt_atomic_production"
    ] = "parity_stub"
    """
    Impurity operator source for DMET-shaped runs (open stack).

    ``parity_stub``: parity ledger uses placeholder dicts. ``whole_active_system``: reuse the global
    active-space ``QubitHamiltonian`` as the impurity (default: exactly one ``fragment_labels`` entry;
    optionally multiple labels when ``dmet_multifragment_one_shot_shared_hamiltonian`` is ``True``).
    ``schmidt_atomic_production``: **Schmidt + spectral bath** impurity Hamiltonian from SCF density
    (see ``schmidt_*`` fields); main-pipeline VQE runs on this impurity ``QubitHamiltonian``, not CASCI active space.
    """
    dmet_target_fragment_electrons: float | None = None
    """Optional DMET-style fragment electron target for μ calibration (Schmidt path when bisection enabled)."""
    schmidt_fragment_atom_indices: list[int] = Field(default_factory=list)
    """Zero-based atom indices for fragment AO seed (required for ``schmidt_atomic_production``)."""
    schmidt_n_bath_spatial: int = 2
    """Number of bath spatial orbitals from environment (D,S) spectral truncation."""
    schmidt_max_impurity_spatial_orbitals: int = 14
    """Hard cap on impurity spatial dimension (FCI / JW cost guard)."""
    schmidt_run_mu_bisection: bool = False
    """If ``True`` and ``dmet_target_fragment_electrons`` is set, bisect μ on fragment diagonal (FCI reference)."""
    schmidt_attach_fci_reference: bool = True
    """Attach small-basis FCI reference energy/1-RDM in audit when impurity spatial count ≤ cap."""
    schmidt_fci_reference_max_spatial_orbitals: int = 8
    """Skip FCI reference block above this impurity spatial size (cost guard)."""
    schmidt_dmet_max_cycles: int = Field(default=1, ge=1, le=256)
    """
    Outer Schmidt/FCI density-feedback iterations (:mod:`~qchem_stack.integrations.schmidt_dmet_self_consistent`).
    ``1`` = single-shot (SCF density only). ``>1`` = iterate bath from mixed global AO density (engineering DMET SCF).
    """
    schmidt_dmet_mixing_alpha: float = Field(default=0.35, gt=0.0, le=1.0)
    """Linear mixing of FCI impurity 1-RDM embedded in AO basis into the global density."""
    schmidt_dmet_convergence_tol: float = Field(default=1e-3, gt=0.0)
    """Stop outer iterations early when :math:`\\| \\mathrm{dm1}_{FCI} - \\gamma \\|_F` falls below this (after cycle 0)."""
    schmidt_multi_fragment_atom_groups: list[list[int]] = Field(default_factory=list)
    """
    If non-empty, **multi-fragment** Gauss–Seidel sweeps (one global ``D``, sequential fragment Schmidt+FCI updates).
    Mutually exclusive with ``schmidt_fragment_atom_indices`` (must leave the latter empty when this is set).
    """
    schmidt_multi_primary_fragment_index: int = Field(default=0, ge=0)
    """Which group in ``schmidt_multi_fragment_atom_groups`` supplies the main-pipeline ``QubitHamiltonian``."""
    schmidt_run_vqe_on_all_fragments: bool = Field(default=False)
    """
    If ``True`` and multi-fragment Schmidt is used, run an **additional** VQE on each fragment impurity
    after the embedding density loop (cost ∝ number of fragments). Default ``False`` for predictable
    production cost; enable when Methods require per-fragment variational energies.
    """
    schmidt_per_fragment_vqe_maxiter: int | None = None
    """Max VQE iterations per fragment; ``None`` means ``quantum.vqe_maxiter``. Bounded when set."""
    dmet_uniform_multifragment_toy: bool = False
    """
    If ``True`` and ``mode==dmet`` with **two or more** fragment labels, run
    :func:`~qchem_stack.integrations.dmet_multifragment_toy.run_uniform_hamiltonian_multifragment_toy`
    (each fragment sees full ``QubitHamiltonian`` — **non-physical**, wiring test only). Off by default.
    Incompatible with ``schmidt_atomic_production``.
    """
    dmet_multifragment_one_shot_shared_hamiltonian: bool = False
    """
    When ``dmet_hamiltonian_source=='whole_active_system'``, allow **multiple** ``fragment_labels`` and run
    :class:`~qchem_stack.integrations.dmet_self_consistent.OneShotEmbeddingDriver` with the **same**
    global ``QubitHamiltonian`` per fragment (demo / reproducibility only).
    """
    dmet_fragment_use_exact_solver: bool = False
    """Dense diagonalization impurity solve for small ``n_qubits`` (see ``dmet_fragment_exact_max_qubits``)."""
    dmet_fragment_exact_max_qubits: int = Field(default=14, ge=1, le=64)
    """Skip dense ED above this qubit count (fragment ledger records ``skipped``)."""
    decomposition_plugin: str = ""
    """Registered toy/plugin name when ``mode=='plugin'`` (e.g. ``uniform_fragment_guess``)."""
    decomposition_plugin_json_path: str | None = None
    """Path to fragment integral JSON (resolved relative to experiment YAML when needed)."""
    schmidt_bath_sidecar_json_path: str | None = None
    """
    Optional JSON merged into ``embedding_workflow.schmidt_bath_sidecar_v1`` when
    ``dmet_hamiltonian_source == 'schmidt_atomic_production'`` (user / Methods audit hook).
    Relative paths resolve against the directory of the experiment YAML when ``cfg_path`` is known.
    """
    oniom_layers_v1: list[dict[str, Any]] = Field(default_factory=list)
    """Toy QM/MM layer hints → ``embedding_workflow.oniom_toy_v1`` (documentation-only)."""

    @field_validator("schmidt_bath_sidecar_json_path")
    @classmethod
    def _strip_bath_sidecar(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s or None

    @field_validator("schmidt_per_fragment_vqe_maxiter")
    @classmethod
    def _schmidt_pf_vqe_maxiter_bounds(cls, v: int | None) -> int | None:
        if v is None:
            return None
        if int(v) < 1 or int(v) > 500_000:
            raise ValueError("schmidt_per_fragment_vqe_maxiter must be in [1, 500000] when set.")
        return int(v)

    @model_validator(mode="after")
    def _dmet_hamiltonian_source_valid(self) -> EmbeddingSpec:
        if self.dmet_hamiltonian_source == "whole_active_system":
            if self.mode != "dmet":
                raise ValueError(
                    "embedding.dmet_hamiltonian_source='whole_active_system' requires embedding.mode='dmet'."
                )
            labs = [x for x in self.fragment_labels if str(x).strip()]
            if self.dmet_multifragment_one_shot_shared_hamiltonian:
                if len(labs) < 2:
                    raise ValueError(
                        "embedding.dmet_multifragment_one_shot_shared_hamiltonian requires at least two "
                        "non-empty embedding.fragment_labels entries."
                    )
            elif len(labs) != 1:
                raise ValueError(
                    "embedding.dmet_hamiltonian_source='whole_active_system' requires exactly one "
                    "non-empty embedding.fragment_labels entry (unless "
                    "dmet_multifragment_one_shot_shared_hamiltonian is True)."
                )
        if self.dmet_hamiltonian_source == "schmidt_atomic_production":
            if self.mode != "dmet":
                raise ValueError(
                    "embedding.dmet_hamiltonian_source='schmidt_atomic_production' requires embedding.mode='dmet'."
                )
            if self.schmidt_multi_fragment_atom_groups:
                if self.schmidt_fragment_atom_indices:
                    raise ValueError(
                        "Use either embedding.schmidt_fragment_atom_indices (single fragment) or "
                        "schmidt_multi_fragment_atom_groups, not both."
                    )
                groups = self.schmidt_multi_fragment_atom_groups
                if any(not gg for gg in groups):
                    raise ValueError("schmidt_multi_fragment_atom_groups: each inner list must be non-empty")
                labs = [x for x in self.fragment_labels if str(x).strip()]
                if labs and len(labs) != len(groups):
                    raise ValueError(
                        "When schmidt_multi_fragment_atom_groups is set, embedding.fragment_labels "
                        "must have the same length as groups (or be empty)."
                    )
                if self.schmidt_multi_primary_fragment_index >= len(groups):
                    raise ValueError("schmidt_multi_primary_fragment_index is out of range for fragment groups")
            else:
                if not self.schmidt_fragment_atom_indices:
                    raise ValueError(
                        "schmidt_atomic_production requires non-empty embedding.schmidt_fragment_atom_indices "
                        "when schmidt_multi_fragment_atom_groups is empty."
                    )
            if self.schmidt_n_bath_spatial < 1:
                raise ValueError("schmidt_n_bath_spatial must be at least 1.")
            if self.schmidt_max_impurity_spatial_orbitals < 2:
                raise ValueError("schmidt_max_impurity_spatial_orbitals must be at least 2.")
        if self.dmet_uniform_multifragment_toy and self.dmet_hamiltonian_source == "schmidt_atomic_production":
            raise ValueError(
                "dmet_uniform_multifragment_toy cannot be combined with schmidt_atomic_production."
            )
        if self.schmidt_run_mu_bisection and self.dmet_target_fragment_electrons is None:
            raise ValueError("schmidt_run_mu_bisection requires embedding.dmet_target_fragment_electrons.")
        return self

    @model_validator(mode="after")
    def _plugin_embedding_requires_fields(self) -> EmbeddingSpec:
        if self.mode == "plugin":
            if not (self.decomposition_plugin or "").strip():
                raise ValueError("embedding.mode='plugin' requires embedding.decomposition_plugin")
            if not (self.decomposition_plugin_json_path or "").strip():
                raise ValueError("embedding.mode='plugin' requires embedding.decomposition_plugin_json_path")
        return self

    @model_validator(mode="after")
    def _projection_mulliken_requires_mode_and_indices(self) -> EmbeddingSpec:
        if self.projection_quantum_hamiltonian == "fragment_mulliken_mo":
            if self.mode != "projection":
                raise ValueError(
                    "embedding.projection_quantum_hamiltonian='fragment_mulliken_mo' requires embedding.mode='projection'."
                )
            if not self.projection_fragment_atom_indices:
                raise ValueError(
                    "embedding.projection_quantum_hamiltonian='fragment_mulliken_mo' requires non-empty "
                    "embedding.projection_fragment_atom_indices."
                )
        return self


class ComputableGraphEdgeDecl(BaseModel):
    """Declare an extra directed edge between computables (match :class:`ComputableRef` ``name``)."""

    from_ref: str
    to_ref: str
    kind: str = "declared_dataflow"


class ComputableGraphEdgeRemove(BaseModel):
    """Remove a semantic/auto edge ``from_ref → to_ref`` (by computable name)."""

    from_ref: str
    to_ref: str


class QuantumSpec(BaseModel):
    """Quantum stage after PySCF + qubit Hamiltonian (InQuanto-style chain).

    Fermion→qubit mapping is selected on :class:`ActiveSpaceSpec` as ``fermion_qubit_mapping``.
    """

    algorithm: str = "vqe"
    """Built-in id (``vqe``, ``adapt``, ``iqeb``, ``tetris_adapt``) or an arbitrary label when ``algorithm_factory`` is set."""
    algorithm_factory: str | None = None
    """Import path ``module.path:callable`` returning a variational runner or plugin (see variational plug-in loader)."""
    variational_ansatz: Literal["hea", "uccsd"] = "hea"
    """``hea``: hardware-efficient layers; ``uccsd``: cluster expansion on JW or BK Hamiltonians (`uccsd_vqe`)."""
    uccsd_trotter_steps: int | None = None
    """If set (>=1) with ``variational_ansatz='uccsd'``, use first-order product-formula layers (see :class:`~qchem_stack.quantum.algorithms.uccsd_vqe.UCCSDTrotterVQE`). ``None`` keeps exact sequential ``expm`` factors per cluster generator."""
    vqe_depth: int = 1
    vqe_maxiter: int = 200
    vqe_optimizer_method: Literal["COBYLA", "L-BFGS-B", "Nelder-Mead"] = "COBYLA"
    """Classical optimizer for variational loops."""
    vqe_initial_parameters_strategy: Literal["random_uniform", "zeros"] = "random_uniform"
    """Initialization of variational parameters before optimization."""
    adapt_max_iter: int = 5
    adapt_pool_id: Literal[
        "fermionic_uccsd",
        "uccsd_jw",
        "uccsd_bravyi_kitaev",
        "uccsd_bk",
        "fermionic_uccsd_bravyi_kitaev",
        "fermionic_uccsd_singles",
        "fermionic_uccsd_doubles_only",
        "fermionic_uccsd_singles_bravyi_kitaev",
        "fermionic_uccsd_doubles_bravyi_kitaev_only",
        "fermionic_uccsd_singles_then_doubles_bk_concat",
        "iqeb_qubit_excitation",
        "qubit_excitation",
        "toy_pair_xx",
    ] = "fermionic_uccsd"
    iqeb_pool_id: Literal[
        "fermionic_uccsd",
        "uccsd_jw",
        "uccsd_bravyi_kitaev",
        "uccsd_bk",
        "fermionic_uccsd_bravyi_kitaev",
        "fermionic_uccsd_singles",
        "fermionic_uccsd_doubles_only",
        "fermionic_uccsd_singles_bravyi_kitaev",
        "fermionic_uccsd_doubles_bravyi_kitaev_only",
        "fermionic_uccsd_singles_then_doubles_bk_concat",
        "iqeb_qubit_excitation",
        "qubit_excitation",
        "toy_pair_xx",
    ] = "iqeb_qubit_excitation"
    iqeb_n_grads: int = Field(default=3, ge=1, le=16)
    iqeb_energy_tolerance: float = 1.0e-8
    iqeb_max_rounds: int = Field(default=2, ge=1, le=64)
    """Outer IQEB rounds (:class:`~qchem_stack.quantum.algorithms.iqeb.IQEBVQE`); ignored unless ``algorithm=='iqeb'``."""
    use_pauli_protocol: bool = True
    pauli_grouping: Literal["tensor_product", "greedy_commuting"] = "tensor_product"
    run_sampled_pauli_protocol: bool = False
    """Monte Carlo energy from grouped Pauli readouts (statevector); see ``PauliAveragingProtocol.run_sampled``."""
    run_qiskit_shots_pauli_protocol: bool = False
    """True: grouped Pauli energy from Qiskit ``get_counts`` bitstrings (Aer or hardware), not statevector MC."""
    record_pauli_measurement_histograms: bool = False
    """With ``run_sampled`` or ``run_qiskit_shots_pauli_protocol``, store per-group histograms in ``protocol_counts``."""
    vqd_after_variational: bool = False
    """If True, run :class:`~qchem_stack.quantum.algorithms.excited.VQD` after VQE/ADAPT/IQEB (same HEA depth)."""
    vqd_n_states: int = 2
    vqd_penalty_weight: float = 5.0
    vqd_overlap_exponent: float = Field(default=1.0, ge=0.5, le=8.0)
    """Penalty uses ``|(s|\\psi)|^{2×exponent}`` summed over pinned reference states."""
    vqd_cobyla_maxiter: int = Field(default=150, ge=1, le=10_000)
    vqd_shots_objective: int = 0
    """Grouped Pauli shot budget per excited level for ``three_protocol.objective`` (0 = exact only)."""
    vqd_shots_overlap: int = 0
    """Swap-test shots per deflation overlap pair (0 = exact overlap only)."""
    vqd_shots_weight: int = 0
    """Reserved for weight-channel Monte Carlo (uses overlap shots when overlap > 0)."""
    qse_after_variational: bool = False
    """If True, run :class:`~qchem_stack.quantum.algorithms.excited.QSE` on the variational HEA reference state."""
    qse_subspace_dim: int = 4
    qse_max_basis: int | None = None
    """If set, passed as ``max_basis`` to QSE basis builders; otherwise uses ``qse_subspace_dim``."""
    qse_shot_mode: Literal["exact", "gaussian_h", "pauli_transitions"] = "exact"
    """``exact``: dense matrix elements; ``gaussian_h``: placeholder noise on :math:`H_{ij}`; ``pauli_transitions``: per-term schedule in ``meta``."""
    qse_shots_per_matrix_element: int = 4096
    """Used when ``qse_shot_mode`` is ``gaussian_h``."""
    qse_shots_per_ij_term: int = 512
    """Used when ``qse_shot_mode`` is ``pauli_transitions``."""
    sceom_after_variational: bool = False
    """If True, run nested-commutator SCEOM :func:`~qchem_stack.quantum.algorithms.sceom.run_sceom_nested_commutator_from_hea`."""
    sceom_subspace_dim: int = 4
    sceom_shots_per_matrix_element: int = 0
    """If > 0, symmetric Gaussian noise on real :math:`M` (placeholder shot model)."""
    sceom_generator_strategy: Literal["legacy", "fermionic_singles_mapped", "pauli_xy_extended"] = "legacy"
    """Excitation generators for SCEOM nested commutators (beyond default toy Paulis)."""
    qpe_demo_track_after_variational: bool = False
    """If True, attach :mod:`qpe_qec_demo` dense Kitaev + Bayesian toy block to pipeline output (no extra deps)."""
    qpe_pipeline_integration: bool = False
    """If True, same as enabling the QPE demo track (alias for dual-track YAML that avoids the longer flag name)."""
    qpe_demo_track_n_bits: int = Field(default=4, ge=2, le=32)
    """QPE demo sidecar: dense Kitaev / energy estimate register width (see ``qpe_demo_track_payload``)."""
    qpe_three_pack_after_variational: bool = False
    """If True, attach dense ``deterministic`` / ``kitaev`` / ``info_theory`` :mod:`qchem_stack.quantum.algorithms.qpe` reports."""
    qpe_three_pack_time: float = Field(default=1.0, gt=0.0, le=1_000_000.0)
    qpe_three_pack_deterministic_rounds: int = Field(default=4, ge=1, le=64)
    qpe_three_pack_kitaev_bits: int = Field(default=6, ge=2, le=32)
    qpe_three_pack_info_samples: int = Field(default=32, ge=1, le=65536)
    vqs_track_after_variational: bool = False
    """If True, run the open-stack VQS/McLachlan toy ODE track using variational angles (``quantum/algorithms/vqs.py``)."""
    vqs_pipeline_integration: bool = False
    """Alias for ``vqs_track_after_variational`` (ergonomic parity YAML, same semantics as QPE dual-track flags)."""
    vqs_mode: Literal["vqs", "mclachlan_real_time", "mclachlan_imag_time"] = "mclachlan_real_time"
    """Which ``vqs`` runner to use on the pipeline track (see :mod:`qchem_stack.quantum.algorithms.vqs_pipeline_track`)."""
    vqs_n_times: int = Field(default=6, ge=2, le=513)
    """Number of ODE time samples (uniform spacing ``vqs_dt``)."""
    vqs_dt: float = Field(default=0.05, gt=0.0, le=10.0)
    """Spacing between consecutive time samples (seconds are a nominal unit; toy dynamics only)."""
    vqs_rhs_mode: Literal["linear_damping", "hea_mclachlan_tdvp"] = "linear_damping"
    """RHS for McLachlan/VQS tracks (`linear_damping` toy flow vs finite-difference HEA TDVP tangent solve)."""
    vqs_tangent_fd_epsilon: float = Field(default=5e-5, gt=0.0, le=1.0)

    def qpe_demo_track_requested(self) -> bool:
        return bool(self.qpe_demo_track_after_variational or self.qpe_pipeline_integration)

    def qpe_three_pack_requested(self) -> bool:
        return bool(self.qpe_three_pack_after_variational)

    def vqs_track_requested(self) -> bool:
        return bool(self.vqs_track_after_variational or self.vqs_pipeline_integration)
    pauli_support_max_terms: int | None = None
    """If set, cap ``protocol_counts['hamiltonian_pauli_strings']`` length; full count in ``n_hamiltonian_pauli_terms_full``."""
    tensornet_expectation_stub: bool = False
    """If True, attach :func:`qchem_stack.tensornet.run_cutensornet_expectation_stub` for CuTensorNet parity rows."""
    tensornet_contraction_engine: Literal[
        "stub", "opt_einsum", "cupy_if_available", "cuquantum_if_available"
    ] = "stub"
    """Tensor-network demo: ``stub``, ``opt_einsum``, ``cupy_if_available``, or ``cuquantum_if_available`` (NVIDIA **cuTensorNet** C API when installed; else explicit fallback status)."""
    computable_extra_edges: list[ComputableGraphEdgeDecl] = Field(default_factory=list)
    """Append DAG edges for workflow preview / UX (open stack; does not change execution order)."""
    computable_remove_edges: list[ComputableGraphEdgeRemove] = Field(default_factory=list)
    """Drop matching auto/semantic edges (e.g. break default excited→Pauli dependency for custom layouts)."""

    @field_validator("algorithm")
    @classmethod
    def _strip_algorithm(cls, v: str) -> str:
        s = str(v).strip()
        if not s:
            raise ValueError("quantum.algorithm must be a non-empty string")
        return s

    @field_validator("algorithm_factory")
    @classmethod
    def _normalize_algorithm_factory(cls, v: str | None) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None

    @model_validator(mode="after")
    def _algorithm_registered_or_factory(self) -> QuantumSpec:
        from qchem_stack.quantum.variational_plugins.loader import validate_factory_import_path
        from qchem_stack.quantum.variational_plugins.registry import is_registered_variational_id

        if self.algorithm_factory:
            validate_factory_import_path(self.algorithm_factory)
            return self
        if not is_registered_variational_id(self.algorithm):
            raise ValueError(
                f"Unknown quantum.algorithm={self.algorithm!r}. "
                "Use a built-in id or set quantum.algorithm_factory to an import path."
            )
        return self

    @model_validator(mode="after")
    def _pauli_shot_mode_mutually_exclusive(self) -> QuantumSpec:
        if self.run_sampled_pauli_protocol and self.run_qiskit_shots_pauli_protocol:
            raise ValueError(
                "Set only one of run_sampled_pauli_protocol (statevector MC) and "
                "run_qiskit_shots_pauli_protocol (Qiskit device/Aer bitstrings), not both."
            )
        return self

    @model_validator(mode="after")
    def _uccsd_trotter_steps_valid(self) -> QuantumSpec:
        t = self.uccsd_trotter_steps
        if t is None:
            return self
        if self.variational_ansatz != "uccsd":
            raise ValueError("quantum.uccsd_trotter_steps is only valid when variational_ansatz='uccsd'.")
        if int(t) < 1:
            raise ValueError("quantum.uccsd_trotter_steps must be >= 1 when set.")
        return self


class ExperimentConfig(BaseModel):
    schema_version: str = "1"
    experiment_id: str
    random_seed: int = 0
    molecule: MoleculeSpec
    scf: SCFSpec = Field(default_factory=SCFSpec)
    active_space: ActiveSpaceSpec
    backend: BackendSpecConfig = Field(default_factory=BackendSpecConfig)
    mitigation: MitigationSpec = Field(default_factory=MitigationSpec)
    compiler: CompilerSpec = Field(default_factory=CompilerSpec)
    quantum: QuantumSpec = Field(default_factory=QuantumSpec)
    embedding: EmbeddingSpec = Field(default_factory=EmbeddingSpec)
    chemistry_extended: ChemistryExtendedSpec = Field(default_factory=ChemistryExtendedSpec)
    nexus_analog: NexusAnalogSpec = Field(default_factory=NexusAnalogSpec)
    nexus_cloud: NexusCloudSpec = Field(default_factory=NexusCloudSpec)
    parity_integrations: ParityIntegrationsSpec = Field(default_factory=ParityIntegrationsSpec)
    md_ml_export: MdMlExportSpec = Field(default_factory=MdMlExportSpec)
    extra: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_yaml_dict(cls, data: dict[str, Any]) -> ExperimentConfig:
        known = {f for f in cls.model_fields}
        top = {k: v for k, v in data.items() if k in known}
        extra_keys = set(data) - known
        if extra_keys:
            top["extra"] = {k: data[k] for k in sorted(extra_keys)}
        return cls.model_validate(top)

    @model_validator(mode="after")
    def _embedding_atom_indices_within_molecule(self) -> ExperimentConfig:
        n_atom = len(self.molecule.symbols)
        for i in self.embedding.projection_fragment_atom_indices:
            if i < 0 or i >= n_atom:
                raise ValueError(
                    f"embedding.projection_fragment_atom_indices: atom index {i} out of range "
                    f"(n_atom={n_atom})."
                )
        return self

    @model_validator(mode="after")
    def _md_ml_extra_coordinates_shape(self) -> ExperimentConfig:
        from qchem_stack.md_bridge.from_pipeline import MD_ML_MAX_EXTRA_GEOMETRIES

        spec = self.md_ml_export
        n_atom = len(self.molecule.symbols)
        if len(spec.extra_coordinates_bohr) > MD_ML_MAX_EXTRA_GEOMETRIES:
            raise ValueError(
                f"md_ml_export.extra_coordinates_bohr: at most {MD_ML_MAX_EXTRA_GEOMETRIES} geometries "
                f"(got {len(spec.extra_coordinates_bohr)})."
            )
        for ei, coords in enumerate(spec.extra_coordinates_bohr):
            if len(coords) != n_atom:
                raise ValueError(
                    f"md_ml_export.extra_coordinates_bohr[{ei}]: expected {n_atom} atoms, got {len(coords)}."
                )
            for ai, row in enumerate(coords):
                if len(row) != 3:
                    raise ValueError(
                        f"md_ml_export.extra_coordinates_bohr[{ei}][{ai}]: expected 3 Cartesian floats."
                    )
        return self

    @model_validator(mode="after")
    def _md_ml_pauli_energy_requires_pauli_protocol(self) -> ExperimentConfig:
        if not self.md_ml_export.attach_single_frame_to_repro:
            return self
        if self.md_ml_export.energy_reference != "pauli_protocol":
            return self
        if not self.quantum.use_pauli_protocol:
            raise ValueError(
                "md_ml_export.energy_reference='pauli_protocol' requires quantum.use_pauli_protocol=true."
            )
        return self

    @model_validator(mode="after")
    def _avas_strategy_requires_pyscf_labels(self) -> ExperimentConfig:
        if self.active_space.strategy != "avas":
            return self
        if str(self.scf.driver).strip().lower() != "pyscf":
            raise ValueError(
                "active_space.strategy='avas' requires a backend that implements PySCF-style AVAS "
                "in this milestone: set scf.driver='pyscf' (or register another adapter whose "
                "SolverCapabilities.supports_avas_active_space_projection is True and wires the same hook). "
                f"Got scf.driver={self.scf.driver!r}."
            )
        if not self.chemistry_extended.avas_ao_labels:
            raise ValueError(
                "active_space.strategy='avas' requires non-empty chemistry_extended.avas_ao_labels "
                "(PySCF AVAS orbital projection inputs)."
            )
        return self

    @model_validator(mode="after")
    def _uccsd_variational_constraints(self) -> ExperimentConfig:
        q = self.quantum
        if q.variational_ansatz != "uccsd":
            return self
        if q.algorithm != "vqe" and not q.algorithm_factory:
            raise ValueError(
                "quantum.variational_ansatz='uccsd' requires quantum.algorithm='vqe' "
                "or an explicit quantum.algorithm_factory (plug-in must honor UCCSD semantics)."
            )
        if self.active_space.fermion_qubit_mapping not in {"jordan_wigner", "bravyi_kitaev"}:
            raise ValueError(
                "quantum.variational_ansatz='uccsd' requires active_space.fermion_qubit_mapping in "
                "{'jordan_wigner', 'bravyi_kitaev'} (square encodings; symmetry_conserving_bravyi_kitaev is unsupported)."
            )
        if q.use_pauli_protocol:
            raise ValueError(
                "quantum.variational_ansatz='uccsd' is incompatible with use_pauli_protocol=True "
                "(Pauli measurement circuits use HEA). Set use_pauli_protocol: false."
            )
        if q.vqd_after_variational or q.qse_after_variational or q.sceom_after_variational:
            raise ValueError(
                "quantum.variational_ansatz='uccsd' cannot combine with VQD/QSE/SCEOM "
                "(those stages expect HEA angle packing)."
            )
        return self


def load_experiment_config(path: str | Path) -> ExperimentConfig:
    p = Path(path)
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in {p}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigurationError(f"Config must be a mapping: {p}")
    return ExperimentConfig.from_yaml_dict(raw)


def _strip_callables(obj: object) -> object:
    """YAML repro dump must not embed runtime callables (e.g. IonStack ``expectation_fn`` tests)."""
    if isinstance(obj, dict):
        return {str(k): _strip_callables(v) for k, v in obj.items() if not callable(v)}
    if isinstance(obj, (list, tuple)):
        return type(obj)(_strip_callables(v) for v in obj if not callable(v))
    return obj


def dump_experiment_config(cfg: ExperimentConfig) -> str:
    raw = _strip_callables(cfg.model_dump(mode="python"))
    return yaml.safe_dump(raw, sort_keys=False, allow_unicode=True)


def backend_spec_from_config(cfg: ExperimentConfig):
    from qchem_stack.backends.spec import BackendSpec

    b = cfg.backend
    return BackendSpec(
        name=b.name,
        provider=b.provider,
        shots_per_circuit=b.shots_per_circuit,
        target_energy_stderr=b.target_energy_stderr,
        qiskit_mode=b.qiskit_mode,
        ionstack_endpoint=b.ionstack_endpoint,
        native_twoq=cfg.compiler.native_twoq,
        meta=dict(b.meta),
    )


def compiler_pass_bundle_from_config(cfg: ExperimentConfig):
    from qchem_stack.backends.spec import CompilerPassBundle

    c = cfg.compiler
    return CompilerPassBundle(
        optimization_level=c.optimization_level,
        preoptimize_passes=list(c.preoptimize_passes),
        compiler_passes=list(c.compiler_passes),
    )


def compiler_bundle_signature_from_config(cfg: ExperimentConfig) -> str:
    """Stable short hash for Methods (pass list + native 2Q + optimization level)."""
    import hashlib
    import json

    c = cfg.compiler
    payload = json.dumps(
        {
            "optimization_level": int(c.optimization_level),
            "native_twoq": str(c.native_twoq),
            "preoptimize_passes": sorted(c.preoptimize_passes),
            "compiler_passes": sorted(c.compiler_passes),
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

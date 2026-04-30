from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from qchem_stack.exceptions import ConfigurationError


class MoleculeSpec(BaseModel):
    symbols: list[str]
    coordinates_bohr: list[list[float]]
    charge: int = 0
    multiplicity: int = 1
    basis: str = "sto-3g"


class SCFSpec(BaseModel):
    driver: Literal["pyscf"] = "pyscf"
    method: Literal["RHF", "ROHF", "UHF"] = "RHF"


class ActiveSpaceSpec(BaseModel):
    n_active_orbitals: int
    n_active_electrons: int


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


class EmbeddingSpec(BaseModel):
    """Falsifiability fields for DMET / projection workflows (chemistry pre-stage)."""

    mode: Literal["none", "dmet", "projection"] = "none"
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

    ``parity_stub``: parity ledger uses placeholder dicts. ``whole_active_system``: **single-fragment
    demo** — exactly one ``fragment_labels`` entry; reuse the global active-space ``QubitHamiltonian``.
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
            if len(labs) != 1:
                raise ValueError(
                    "embedding.dmet_hamiltonian_source='whole_active_system' requires exactly one "
                    "non-empty embedding.fragment_labels entry."
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
    """Quantum stage after PySCF + JW Hamiltonian (InQuanto-style chain)."""

    algorithm: Literal["vqe", "adapt", "iqeb"] = "vqe"
    vqe_depth: int = 1
    vqe_maxiter: int = 200
    adapt_max_iter: int = 5
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
    qpe_demo_track_after_variational: bool = False
    """If True, attach :mod:`qpe_qec_demo` dense Kitaev + Bayesian toy block to pipeline output (no extra deps)."""
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

    @model_validator(mode="after")
    def _pauli_shot_mode_mutually_exclusive(self) -> QuantumSpec:
        if self.run_sampled_pauli_protocol and self.run_qiskit_shots_pauli_protocol:
            raise ValueError(
                "Set only one of run_sampled_pauli_protocol (statevector MC) and "
                "run_qiskit_shots_pauli_protocol (Qiskit device/Aer bitstrings), not both."
            )
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


def load_experiment_config(path: str | Path) -> ExperimentConfig:
    p = Path(path)
    try:
        raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in {p}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ConfigurationError(f"Config must be a mapping: {p}")
    return ExperimentConfig.from_yaml_dict(raw)


def dump_experiment_config(cfg: ExperimentConfig) -> str:
    return yaml.safe_dump(cfg.model_dump(mode="json"), sort_keys=False, allow_unicode=True)


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

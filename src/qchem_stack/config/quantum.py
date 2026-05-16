"""Quantum-stage algorithm configuration and cross-field validation guards."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from ._quantum_validation import (
    validate_algorithm_registered_or_factory,
    validate_pauli_shot_mode_mutually_exclusive,
    validate_uccsd_trotter_steps,
    validate_vqd_max_overlap_warn_nonneg,
    validate_vqd_penalty_weights_len,
)
from ._validation import strip_optional_text, strip_required_text

OperatorPoolId = Literal[
    "fermionic_uccsd",
    "uccsd_jw",
    "uccsd_singles",
    "uccsd_doubles_only",
    "uccsd_bravyi_kitaev",
    "uccsd_bk",
    "uccsd_bk_singles",
    "uccsd_bk_doubles_only",
    "uccsd_bk_singles_then_doubles",
    "fermionic_uccsd_bravyi_kitaev",
    "fermionic_uccsd_singles",
    "fermionic_uccsd_doubles_only",
    "fermionic_uccsd_singles_bravyi_kitaev",
    "fermionic_uccsd_doubles_bravyi_kitaev_only",
    "fermionic_uccsd_singles_then_doubles_bk_concat",
    "iqeb_qubit_excitation",
    "qubit_excitation",
    "toy_pair_xx",
]


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
    """Quantum stage after PySCF + qubit Hamiltonian (instantiate/build/run/evaluate chain).

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
    adapt_pool_id: OperatorPoolId = "fermionic_uccsd"
    iqeb_pool_id: OperatorPoolId = "iqeb_qubit_excitation"
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
    """If True, run :class:`~qchem_stack.quantum.algorithms.excited.VQD` after the variational stage."""
    vqd_n_states: int = 2
    vqd_penalty_weight: float = 5.0
    """Scalar penalty λ when ``vqd_penalty_weights`` is unset (Higgott-style overlap sum)."""
    vqd_penalty_weights: list[float] | None = None
    """Optional per deflation level ``λ_{level}`` (length ``vqd_n_states - 1``); overrides scalar weight."""
    vqd_overlap_exponent: float = Field(default=1.0, ge=0.5, le=8.0)
    """Penalty uses ``|(s|\\psi)|^{2×exponent}`` summed over pinned reference states."""
    vqd_cobyla_maxiter: int = Field(default=150, ge=1, le=10_000)
    """Max iterations passed to SciPy for **all** VQD optimizer methods (historical name)."""
    vqd_optimizer_method: Literal["COBYLA", "L-BFGS-B", "Nelder-Mead"] = "COBYLA"
    """Classical optimizer for VQD inner loops (single collapsed objective)."""
    vqd_init_strategy: Literal[
        "legacy",
        "reuse_ground_perturb",
        "previous_layer_perturb",
        "random_uniform",
    ] = "legacy"
    """``legacy``: match pre-2026 behavior (first excited starts from ground angles when shapes match)."""
    vqd_init_noise_scale: float = Field(default=0.15, ge=0.0)
    """Gaussian σ for ``reuse_ground_perturb`` / ``previous_layer_perturb`` (radians-scale)."""
    vqd_max_overlap_warn: float | None = Field(default=0.05)
    """Emit ``meta.vqd_warnings`` when summed squared overlaps exceed this; ``None`` disables."""
    vqd_overlap_mode: Literal["statevector_overlap", "tangelo_circuit_analogy"] = (
        "statevector_overlap"
    )
    """Overlap semantics selector for VQD metadata/export (current executor path remains statevector)."""
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
    sceom_generator_strategy: Literal["legacy", "fermionic_singles_mapped", "pauli_xy_extended"] = (
        "legacy"
    )
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
        return strip_required_text(v, field_name="quantum.algorithm")

    @field_validator("algorithm_factory")
    @classmethod
    def _normalize_algorithm_factory(cls, v: str | None) -> str | None:
        return strip_optional_text(v)

    @model_validator(mode="after")
    def _algorithm_registered_or_factory(self) -> QuantumSpec:
        validate_algorithm_registered_or_factory(self)
        return self

    @model_validator(mode="after")
    def _pauli_shot_mode_mutually_exclusive(self) -> QuantumSpec:
        validate_pauli_shot_mode_mutually_exclusive(self)
        return self

    @model_validator(mode="after")
    def _uccsd_trotter_steps_valid(self) -> QuantumSpec:
        validate_uccsd_trotter_steps(self)
        return self

    @model_validator(mode="after")
    def _vqd_penalty_weights_len(self) -> QuantumSpec:
        validate_vqd_penalty_weights_len(self)
        return self

    @field_validator("vqd_max_overlap_warn")
    @classmethod
    def _vqd_max_overlap_warn_nonneg(cls, v: float | None) -> float | None:
        return validate_vqd_max_overlap_warn_nonneg(v)

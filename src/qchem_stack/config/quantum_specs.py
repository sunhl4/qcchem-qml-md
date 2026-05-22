"""Nested quantum-stage sub-schemas (YAML path = Python path)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .quantum_enums import OperatorPoolId
from .quantum_graph import (  # noqa: TC001 — Pydantic resolves graph edge types at runtime
    ComputableGraphEdgeDecl,
    ComputableGraphEdgeRemove,
)

_FORBID = ConfigDict(extra="forbid")


class QuantumVariationalSpec(BaseModel):
    model_config = _FORBID

    ansatz: Literal["hea", "uccsd"] = Field(
        default="hea",
        description="Variational ansatz: hea layers or uccsd cluster expansion.",
    )
    uccsd_trotter_steps: int | None = Field(
        default=None,
        description="Optional UCCSD first-order Trotter layer count (uccsd ansatz only).",
    )


class QuantumUccsdSpec(BaseModel):
    model_config = _FORBID

    decomposition_mode: Literal["pauli", "unitary"] = Field(
        default="pauli",
        description="UCCSD CircuitIR prep: pauli rotation chains or dense unitary blocks.",
    )


class QuantumVqeSpec(BaseModel):
    model_config = _FORBID

    depth: int = Field(default=1, ge=1, description="HEA layer depth for VQE.")
    maxiter: int = Field(default=200, ge=1, description="Classical optimizer iteration budget.")
    optimizer_method: Literal["COBYLA", "L-BFGS-B", "Nelder-Mead"] = Field(
        default="COBYLA",
        description="SciPy optimizer for variational loops.",
    )
    initial_parameters_strategy: Literal["random_uniform", "zeros"] = Field(
        default="random_uniform",
        description="Initial angle vector before optimization.",
    )


class QuantumAdaptSpec(BaseModel):
    model_config = _FORBID

    max_iter: int = Field(default=5, ge=1, description="ADAPT outer iteration cap.")
    pool_id: OperatorPoolId = Field(
        default=OperatorPoolId.FERMIONIC_UCCSD,
        description="Operator pool for ADAPT / tetris_adapt.",
    )


class QuantumIqebSpec(BaseModel):
    model_config = _FORBID

    pool_id: OperatorPoolId = Field(
        default=OperatorPoolId.IQEB_QUBIT_EXCITATION,
        description="Operator pool for IQEB rounds.",
    )
    n_grads: int = Field(default=3, ge=1, le=16, description="Gradients per IQEB round.")
    energy_tolerance: float = Field(
        default=1.0e-8, gt=0.0, description="IQEB energy convergence tol."
    )
    max_rounds: int = Field(default=2, ge=1, le=64, description="Outer IQEB round cap.")


class QuantumPauliSpec(BaseModel):
    model_config = _FORBID

    use_protocol: bool = Field(default=True, description="Enable Pauli averaging protocol stage.")
    grouping: Literal["tensor_product", "greedy_commuting"] = Field(
        default="tensor_product",
        description="Pauli string grouping strategy.",
    )
    run_sampled: bool = Field(
        default=False,
        description="Statevector Monte Carlo grouped Pauli energy.",
    )
    run_qiskit_shots: bool = Field(
        default=False,
        description="Qiskit device/Aer bitstring Pauli energy.",
    )
    record_histograms: bool = Field(
        default=False,
        description="Store per-group measurement histograms in protocol_counts.",
    )
    support_max_terms: int | None = Field(
        default=None,
        ge=1,
        description="Cap exported hamiltonian_pauli_strings length when set.",
    )


class QuantumExcitedVqdSpec(BaseModel):
    model_config = _FORBID

    after_variational: bool = Field(default=False, description="Run VQD after variational stage.")
    n_states: int = Field(default=2, ge=2, description="Number of states including ground.")
    penalty_weight: float = Field(
        default=5.0, ge=0.0, description="Scalar overlap penalty when weights unset."
    )
    penalty_weights: list[float] | None = Field(
        default=None,
        description="Per-level penalty weights (length n_states - 1).",
    )
    overlap_exponent: float = Field(
        default=1.0, ge=0.5, le=8.0, description="Overlap penalty exponent."
    )
    cobyla_maxiter: int = Field(
        default=150, ge=1, le=10_000, description="Optimizer maxiter for VQD."
    )
    optimizer_method: Literal["COBYLA", "L-BFGS-B", "Nelder-Mead"] = Field(
        default="COBYLA",
        description="Classical optimizer for VQD inner loops.",
    )
    init_strategy: Literal[
        "legacy",
        "reuse_ground_perturb",
        "previous_layer_perturb",
        "random_uniform",
    ] = Field(default="legacy", description="Excited-state angle initialization strategy.")
    init_noise_scale: float = Field(
        default=0.15, ge=0.0, description="Gaussian noise for perturb init."
    )
    max_overlap_warn: float | None = Field(
        default=0.05,
        description="Warn when summed squared overlaps exceed threshold; null disables.",
    )
    overlap_mode: Literal["statevector_overlap", "tangelo_circuit_analogy", "deflation_circuit"] = (
        Field(
            default="statevector_overlap",
            description="Overlap semantics for metadata/export.",
        )
    )
    optimizer_mode: Literal["collapsed", "three_computable"] = Field(
        default="collapsed",
        description="collapsed: single objective; three_computable: decoupled channel evaluation.",
    )
    shots_objective: int = Field(
        default=0, ge=0, description="Pauli shots per excited level (0=exact)."
    )
    shots_overlap: int = Field(default=0, ge=0, description="Swap-test shots per overlap pair.")
    shots_weight: int = Field(default=0, ge=0, description="Reserved weight-channel shot budget.")


class QuantumExcitedQseSpec(BaseModel):
    model_config = _FORBID

    after_variational: bool = Field(default=False, description="Run QSE after variational stage.")
    subspace_dim: int = Field(default=4, ge=1, description="QSE subspace dimension.")
    max_basis: int | None = Field(default=None, ge=1, description="Optional max_basis override.")
    shot_mode: Literal["exact", "gaussian_h", "pauli_transitions", "pauli_transitions_qiskit"] = (
        Field(
            default="exact",
            description="QSE matrix element evaluation mode.",
        )
    )
    expansion_pool: Literal["fermionic_singles", "fermionic_singles_doubles"] = Field(
        default="fermionic_singles",
        description="UCCSD QSE basis pool.",
    )
    shots_per_matrix_element: int = Field(
        default=4096, ge=1, description="Shots for gaussian_h mode."
    )
    shots_per_ij_term: int = Field(
        default=512, ge=1, description="Shots per term in pauli_transitions."
    )


class QuantumExcitedSceomSpec(BaseModel):
    model_config = _FORBID

    after_variational: bool = Field(default=False, description="Run SCEOM after variational stage.")
    subspace_dim: int = Field(default=4, ge=1, description="SCEOM subspace dimension.")
    shots_per_matrix_element: int = Field(
        default=0,
        ge=0,
        description="Gaussian noise shots on M when > 0.",
    )
    generator_strategy: Literal["legacy", "fermionic_singles_mapped", "pauli_xy_extended"] = Field(
        default="fermionic_singles_mapped",
        description="SCEOM excitation generator strategy.",
    )
    self_consistent_rounds: int = Field(
        default=0,
        ge=0,
        le=4,
        description="Optional SCEOM self-consistent iterations after M diagonalization.",
    )
    shots_backend: Literal["statevector", "qiskit"] = Field(
        default="statevector",
        description="Shot backend for SCEOM M-matrix elements when shots_per_matrix_element > 0.",
    )


class QuantumExcitedSpec(BaseModel):
    model_config = _FORBID

    vqd: QuantumExcitedVqdSpec = Field(default_factory=QuantumExcitedVqdSpec)
    qse: QuantumExcitedQseSpec = Field(default_factory=QuantumExcitedQseSpec)
    sceom: QuantumExcitedSceomSpec = Field(default_factory=QuantumExcitedSceomSpec)


class QuantumQpeThreePackSpec(BaseModel):
    model_config = _FORBID

    after_variational: bool = Field(
        default=False, description="Attach dense QPE three-pack reports."
    )
    time: float = Field(
        default=1.0, gt=0.0, le=1_000_000.0, description="Evolution time parameter."
    )
    deterministic_rounds: int = Field(
        default=4, ge=1, le=64, description="Deterministic QPE rounds."
    )
    kitaev_bits: int = Field(default=6, ge=2, le=32, description="Kitaev register width.")
    info_samples: int = Field(default=32, ge=1, le=65536, description="Info-theory sample count.")


class QuantumQpeDemoSpec(BaseModel):
    model_config = _FORBID

    track_after_variational: bool = Field(
        default=False, description="Attach QPE demo sidecar track."
    )
    pipeline_integration: bool = Field(
        default=False,
        description="Alias enabling QPE demo track (parity YAML ergonomics).",
    )
    demo_track_n_bits: int = Field(
        default=4, ge=2, le=32, description="Demo register width in bits."
    )
    three_pack: QuantumQpeThreePackSpec = Field(default_factory=QuantumQpeThreePackSpec)

    def track_requested(self) -> bool:
        return bool(self.track_after_variational or self.pipeline_integration)

    def three_pack_requested(self) -> bool:
        return bool(self.three_pack.after_variational)


class QuantumVqsDemoSpec(BaseModel):
    model_config = _FORBID

    track_after_variational: bool = Field(
        default=False, description="Run VQS/McLachlan toy ODE track."
    )
    pipeline_integration: bool = Field(
        default=False,
        description="Alias enabling VQS track (parity YAML ergonomics).",
    )
    mode: Literal["vqs", "mclachlan_real_time", "mclachlan_imag_time"] = Field(
        default="mclachlan_real_time",
        description="VQS runner mode.",
    )
    n_times: int = Field(default=6, ge=2, le=513, description="Number of ODE time samples.")
    dt: float = Field(default=0.05, gt=0.0, le=10.0, description="Time spacing between samples.")
    rhs_mode: Literal["linear_damping", "hea_mclachlan_tdvp"] = Field(
        default="linear_damping",
        description="ODE right-hand side mode.",
    )
    tangent_fd_epsilon: float = Field(
        default=5e-5,
        gt=0.0,
        le=1.0,
        description="Finite-difference epsilon for HEA McLachlan TDVP.",
    )

    def track_requested(self) -> bool:
        return bool(self.track_after_variational or self.pipeline_integration)


class QuantumDemosSpec(BaseModel):
    model_config = _FORBID

    qpe: QuantumQpeDemoSpec = Field(default_factory=QuantumQpeDemoSpec)
    vqs: QuantumVqsDemoSpec = Field(default_factory=QuantumVqsDemoSpec)


class QuantumTensornetSpec(BaseModel):
    model_config = _FORBID

    expectation_stub: bool = Field(
        default=False, description="Attach CuTensorNet expectation stub."
    )
    contraction_engine: Literal[
        "stub", "opt_einsum", "cupy_if_available", "cuquantum_if_available"
    ] = Field(default="stub", description="Tensor-network contraction backend selector.")


class QuantumGraphSpec(BaseModel):
    model_config = _FORBID

    extra_edges: list[ComputableGraphEdgeDecl] = Field(
        default_factory=list,
        description="Extra DAG edges for workflow preview only.",
    )
    remove_edges: list[ComputableGraphEdgeRemove] = Field(
        default_factory=list,
        description="Edges to remove from auto/semantic graph.",
    )

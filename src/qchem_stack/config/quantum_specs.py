"""Nested quantum-stage sub-schemas (YAML path = Python path)."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import ForbidExtraBase
from .quantum_enums import OperatorPoolId
from .quantum_graph import (  # noqa: TC001 — Pydantic resolves graph edge types at runtime
    ComputableGraphEdgeDecl,
    ComputableGraphEdgeRemove,
)


class QuantumVariationalSpec(ForbidExtraBase):
    ansatz: Literal[
        "hea",
        "uccsd",
        "uccgd",
        "qcc",
        "upccgsd",
        "puccd",
        "iqcc",
        "qite",
        "vsqs",
    ] = Field(
        default="hea",
        description=(
            "Variational ansatz: HEA, cluster ansätze, qcc, iqcc/qite research plugins, or VSQS schedule."
        ),
    )
    uccsd_trotter_steps: int | None = Field(
        default=None,
        description="Optional UCCSD first-order Trotter layer count (uccsd ansatz only).",
    )
    vsqs_intervals: int = Field(
        default=2,
        ge=2,
        description="VSQS schedule steps (must be > 1).",
    )
    vsqs_time: float = Field(
        default=1.0,
        gt=0.0,
        description="Total VSQS propagation time.",
    )
    vsqs_trotter_order: Literal[1, 2] = Field(
        default=1,
        description="Trotter order for VSQS Pauli-sum layers.",
    )


class QuantumUccsdSpec(ForbidExtraBase):
    decomposition_mode: Literal["pauli", "unitary"] = Field(
        default="pauli",
        description="UCCSD CircuitIR prep: pauli rotation chains or dense unitary blocks.",
    )


class QuantumVqeSpec(ForbidExtraBase):
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


class QuantumGqeSpec(ForbidExtraBase):
    """Generative Quantum Eigensolver knobs (peer algorithm family to VQE)."""

    n_gates: int = Field(default=8, ge=1, le=128, description="Generated circuit token length.")
    max_iters: int = Field(default=25, ge=1, description="GQE outer training iterations.")
    batch_size: int = Field(default=8, ge=1, le=256, description="Sequences sampled per iteration.")
    buffer_size: int = Field(default=64, ge=1, description="Replay buffer capacity.")
    learning_rate: float = Field(default=5.0e-3, gt=0.0, description="Adam step size for policy.")
    beta: float = Field(default=5.0, gt=0.0, description="Initial inverse temperature.")
    beta_min: float = Field(default=0.5, gt=0.0, description="β schedule floor.")
    beta_max: float = Field(default=20.0, gt=0.0, description="β schedule ceiling.")
    loss: Literal["lm", "grpo", "dpo", "pdpo", "wmse"] = Field(
        default="grpo",
        description="Policy loss: Logit Matching / GRPO / DPO / Persistent-DPO / WMSE.",
    )
    grpo_clip: float = Field(default=0.2, gt=0.0, le=1.0, description="GRPO ratio clip ε.")
    pdpo_alpha: float = Field(default=0.1, ge=0.0, le=1.0, description="Persistent-DPO α.")
    dpo_beta: float = Field(default=0.1, gt=0.0, description="DPO / P-DPO temperature.")
    pool_mode: Literal["hamiltonian_pauli", "uccsd", "spin_heisenberg", "simple"] = Field(
        default="hamiltonian_pauli",
        description="Operator-pool construction mode.",
    )
    embed_dim: int = Field(default=16, ge=2, le=256, description="Policy embedding dimension.")
    qcc_budget: float | None = Field(
        default=None,
        description="Optional circuit-cutting cost budget (A2); None disables masking.",
    )
    qsci_subspace_size: int = Field(
        default=8, ge=1, le=256, description="QSCI determinant subspace size (A4/A6)."
    )
    condition_dim: int = Field(
        default=0, ge=0, le=256, description="Conditional-GQE condition vector size (A1)."
    )
    energy_offset: float = Field(
        default=0.0, description="Logit-matching energy offset (Nakaji N₂ stability)."
    )
    backbone: Literal["linear", "kan"] = Field(
        default="linear",
        description="Classical generative backbone (KAN used by GQKAE).",
    )


class QuantumSqdSpec(ForbidExtraBase):
    """Sample-based quantum chemistry knobs (SQD / QSCI family; peer to VQE).

    Dense statevector prototypes only (≤12 qubits). Customer ids: ``cbs`` /
    ``qsci`` / ``sqd`` / ``skqd`` / ``sqdrift``. Experimental lite ids require
    ``allow_experimental: true``.
    """

    n_shots: int = Field(default=512, ge=1, description="Computational-basis shots per sample round.")
    subspace_size: int = Field(default=16, ge=1, le=4096, description="Selected CI determinant count.")
    max_iters: int = Field(default=5, ge=1, description="Outer iterative SQD / HI-VQE / ADAPT rounds.")
    hea_depth: int = Field(default=1, ge=1, le=16, description="HEA depth for sampling preparation.")
    n_electrons: int | None = Field(
        default=None,
        description="Particle-number sector; None uses Hamiltonian fermion_space when present.",
    )
    krylov_dim: int = Field(default=4, ge=1, le=64, description="SKQD Krylov basis size.")
    krylov_dt: float = Field(default=0.3, gt=0.0, description="SKQD time step for Krylov powers.")
    qdrift_steps: int = Field(default=8, ge=1, description="SqDRIFT qDRIFT steps per replica.")
    qdrift_replicas: int = Field(default=4, ge=1, description="SqDRIFT independent channel replicas.")
    recovery_iters: int = Field(default=3, ge=0, description="S-CORE-lite occupancy recovery passes.")
    n_fragments: int = Field(default=2, ge=1, le=32, description="EWF / QBE fragment count (lite).")
    afqmc_walkers: int = Field(
        default=32,
        ge=1,
        description="Walker count for sqd_afqmc_lite subspace refinement (not ph-AFQMC).",
    )
    afqmc_steps: int = Field(
        default=20,
        ge=1,
        description="Iteration count for sqd_afqmc_lite subspace refinement (not ph-AFQMC).",
    )
    energy_tol: float = Field(default=1.0e-5, gt=0.0, description="Iterative energy convergence tol.")
    carryover: int = Field(default=4, ge=0, description="Configs carried across SQD iterations.")
    allow_experimental: bool = Field(
        default=False,
        description=(
            "Opt in to experimental SQD ids (adapt_qsci, *_lite embedding/AFQMC/QSE demos). "
            "Customer-supported ids do not require this flag."
        ),
    )


class QuantumAdaptSpec(ForbidExtraBase):
    max_iter: int = Field(default=5, ge=1, description="ADAPT outer iteration cap.")
    pool_id: OperatorPoolId = Field(
        default=OperatorPoolId.FERMIONIC_UCCSD,
        description="Operator pool for ADAPT / tetris_adapt.",
    )
    grad_tol: float = Field(
        default=1.0e-2,
        gt=0.0,
        description="Stop ADAPT when best pool-gradient magnitude falls below this threshold.",
    )


class QuantumIqebSpec(ForbidExtraBase):
    pool_id: OperatorPoolId = Field(
        default=OperatorPoolId.IQEB_QUBIT_EXCITATION,
        description="Operator pool for IQEB rounds.",
    )
    n_grads: int = Field(default=3, ge=1, le=16, description="Gradients per IQEB round.")
    energy_tolerance: float = Field(
        default=1.0e-8, gt=0.0, description="IQEB energy convergence tol."
    )
    max_rounds: int = Field(default=2, ge=1, le=64, description="Outer IQEB round cap.")


class QuantumPauliSpec(ForbidExtraBase):
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


class QuantumExcitedVqdSpec(ForbidExtraBase):
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


class QuantumExcitedQseSpec(ForbidExtraBase):
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


class QuantumExcitedSceomSpec(ForbidExtraBase):
    after_variational: bool = Field(default=False, description="Run SCEOM after variational stage.")
    subspace_dim: int = Field(default=4, ge=1, description="SCEOM subspace dimension.")
    shots_per_matrix_element: int = Field(
        default=0,
        ge=0,
        description="Gaussian noise shots on M when > 0.",
    )
    generator_strategy: Literal[
        "legacy",
        "fermionic_singles_mapped",
        "pauli_xy_extended",
        "symmetry_filtered_partial",
    ] = Field(
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


class QuantumExcitedSpec(ForbidExtraBase):
    vqd: QuantumExcitedVqdSpec = Field(default_factory=QuantumExcitedVqdSpec)
    qse: QuantumExcitedQseSpec = Field(default_factory=QuantumExcitedQseSpec)
    sceom: QuantumExcitedSceomSpec = Field(default_factory=QuantumExcitedSceomSpec)


class QuantumQpeThreePackSpec(ForbidExtraBase):
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


class QuantumQpeDemoSpec(ForbidExtraBase):
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


class QuantumVqsDemoSpec(ForbidExtraBase):
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


class QuantumDemosSpec(ForbidExtraBase):
    qpe: QuantumQpeDemoSpec = Field(default_factory=QuantumQpeDemoSpec)
    vqs: QuantumVqsDemoSpec = Field(default_factory=QuantumVqsDemoSpec)


class QuantumTensornetSpec(ForbidExtraBase):
    expectation_stub: bool = Field(
        default=False, description="Attach CuTensorNet expectation stub."
    )
    contraction_engine: Literal[
        "stub", "opt_einsum", "cupy_if_available", "cuquantum_if_available"
    ] = Field(default="stub", description="Tensor-network contraction backend selector.")


class QuantumGraphSpec(ForbidExtraBase):
    extra_edges: list[ComputableGraphEdgeDecl] = Field(
        default_factory=list,
        description="Extra DAG edges for workflow preview only.",
    )
    remove_edges: list[ComputableGraphEdgeRemove] = Field(
        default_factory=list,
        description="Edges to remove from auto/semantic graph.",
    )

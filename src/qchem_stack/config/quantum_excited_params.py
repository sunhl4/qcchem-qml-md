"""Excited-state plugin params and variational follow-on helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from .experiment import ExperimentConfig

from .quantum_resolvers import quantum_repro_sidecar_fields


class ExcitedVqdPluginParams(TypedDict):
    n_states: int
    penalty_weight: float
    penalty_weights: list[float] | None
    overlap_exponent: float
    cobyla_maxiter: int
    optimizer_method: Literal["COBYLA", "L-BFGS-B", "Nelder-Mead"]
    init_strategy: Literal[
        "legacy", "reuse_ground_perturb", "previous_layer_perturb", "random_uniform"
    ]
    init_noise_scale: float
    max_overlap_warn: float | None
    overlap_mode: Literal["statevector_overlap", "tangelo_circuit_analogy", "deflation_circuit"]
    optimizer_mode: Literal["collapsed", "three_computable"]
    shots_objective: int
    shots_overlap: int
    shots_weight: int


class ExcitedQsePluginParams(TypedDict):
    subspace_dim: int
    max_basis: int | None
    shot_mode: Literal["exact", "gaussian_h", "pauli_transitions", "pauli_transitions_qiskit"]
    expansion_pool: str
    shots_per_matrix_element: int
    shots_per_ij_term: int


class ExcitedSceomPluginParams(TypedDict):
    generator_strategy: Literal[
        "legacy",
        "fermionic_singles_mapped",
        "pauli_xy_extended",
        "symmetry_filtered_partial",
    ]
    subspace_dim: int
    shots_per_matrix_element: int
    self_consistent_rounds: int
    shots_backend: Literal["statevector", "qiskit"]


class VqsTrackPayloadKwargs(TypedDict):
    mode: Literal["vqs", "mclachlan_real_time", "mclachlan_imag_time"]
    n_times: int
    dt: float
    rhs_mode_yaml: Literal["linear_damping", "hea_mclachlan_tdvp"]
    tangent_fd_epsilon_yaml: float


def resolve_excited_vqd_n_states(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.excited.vqd.n_states)


def resolve_excited_qse_subspace_dim(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.excited.qse.subspace_dim)


def resolve_excited_sceom_subspace_dim(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.excited.sceom.subspace_dim)


def excited_sceom_plugin_params(cfg: ExperimentConfig) -> ExcitedSceomPluginParams:
    s = cfg.quantum.excited.sceom
    return {
        "generator_strategy": s.generator_strategy,
        "subspace_dim": s.subspace_dim,
        "shots_per_matrix_element": s.shots_per_matrix_element,
        "self_consistent_rounds": s.self_consistent_rounds,
        "shots_backend": s.shots_backend,
    }


def excited_vqd_plugin_params(cfg: ExperimentConfig) -> ExcitedVqdPluginParams:
    v = cfg.quantum.excited.vqd
    return {
        "n_states": v.n_states,
        "penalty_weight": v.penalty_weight,
        "penalty_weights": v.penalty_weights,
        "overlap_exponent": v.overlap_exponent,
        "cobyla_maxiter": v.cobyla_maxiter,
        "optimizer_method": v.optimizer_method,
        "init_strategy": v.init_strategy,
        "init_noise_scale": v.init_noise_scale,
        "max_overlap_warn": v.max_overlap_warn,
        "overlap_mode": v.overlap_mode,
        "optimizer_mode": v.optimizer_mode,
        "shots_objective": v.shots_objective,
        "shots_overlap": v.shots_overlap,
        "shots_weight": v.shots_weight,
    }


def excited_qse_plugin_params(cfg: ExperimentConfig) -> ExcitedQsePluginParams:
    qse = cfg.quantum.excited.qse
    return {
        "subspace_dim": qse.subspace_dim,
        "max_basis": qse.max_basis,
        "shot_mode": qse.shot_mode,
        "expansion_pool": qse.expansion_pool,
        "shots_per_matrix_element": qse.shots_per_matrix_element,
        "shots_per_ij_term": qse.shots_per_ij_term,
    }


def excited_vqd_after_variational(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.excited.vqd.after_variational)


def excited_qse_after_variational(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.excited.qse.after_variational)


def excited_sceom_after_variational(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.excited.sceom.after_variational)


def excited_any_after_variational(cfg: ExperimentConfig) -> bool:
    return (
        excited_vqd_after_variational(cfg)
        or excited_qse_after_variational(cfg)
        or excited_sceom_after_variational(cfg)
    )


def quantum_excited_run_summary_yaml_fields(cfg: ExperimentConfig) -> dict[str, object]:
    """Excited-state YAML keys copied into ``run_summary`` when bundles are present."""
    side = quantum_repro_sidecar_fields(cfg)
    return {
        "vqd_n_states_yaml": side["vqd_n_states"],
        "vqd_overlap_exponent_yaml": side["vqd_overlap_exponent_yaml"],
        "vqd_cobyla_maxiter_yaml": side["vqd_cobyla_maxiter_yaml"],
        "vqd_optimizer_method_yaml": side["vqd_optimizer_method_yaml"],
        "vqd_init_strategy_yaml": side["vqd_init_strategy_yaml"],
        "vqd_overlap_mode_yaml": side["vqd_overlap_mode_yaml"],
        "qse_shot_mode": side["qse_shot_mode"],
        "qse_subspace_dim_yaml": side["qse_subspace_dim"],
        "qse_max_basis_yaml": side["qse_max_basis"],
        "sceom_shots_per_matrix_element": side["sceom_shots_per_matrix_element"],
        "sceom_subspace_dim_yaml": side["sceom_subspace_dim"],
        "sceom_generator_strategy_yaml": side["sceom_generator_strategy_yaml"],
    }

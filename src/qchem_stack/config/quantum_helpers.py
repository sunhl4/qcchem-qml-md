"""Read-only helpers for :class:`~qchem_stack.config.quantum.QuantumSpec`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from .experiment import ExperimentConfig


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
    overlap_mode: Literal["statevector_overlap", "tangelo_circuit_analogy"]
    shots_objective: int
    shots_overlap: int
    shots_weight: int


class ExcitedQsePluginParams(TypedDict):
    subspace_dim: int
    max_basis: int | None
    shot_mode: Literal["exact", "gaussian_h", "pauli_transitions"]
    shots_per_matrix_element: int
    shots_per_ij_term: int


class ExcitedSceomPluginParams(TypedDict):
    generator_strategy: Literal["legacy", "fermionic_singles_mapped", "pauli_xy_extended"]
    subspace_dim: int
    shots_per_matrix_element: int


class VqsTrackPayloadKwargs(TypedDict):
    mode: Literal["vqs", "mclachlan_real_time", "mclachlan_imag_time"]
    n_times: int
    dt: float
    rhs_mode_yaml: Literal["linear_damping", "hea_mclachlan_tdvp"]
    tangent_fd_epsilon_yaml: float


def resolve_variational_algorithm(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.algorithm).strip()


def resolve_vqe_depth(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.vqe.depth)


def resolve_vqe_maxiter(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.vqe.maxiter)


def resolve_variational_ansatz(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.variational.ansatz)


def resolve_uccsd_trotter_steps(cfg: ExperimentConfig) -> int | None:
    return cfg.quantum.variational.uccsd_trotter_steps


def resolve_vqe_optimizer_method(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.vqe.optimizer_method)


def resolve_vqe_initial_parameters_strategy(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.vqe.initial_parameters_strategy)


def resolve_adapt_max_iter(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.adapt.max_iter)


def resolve_adapt_pool_id(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.adapt.pool_id)


def resolve_iqeb_max_rounds(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.iqeb.max_rounds)


def resolve_iqeb_pool_id(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.iqeb.pool_id)


def resolve_iqeb_n_grads(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.iqeb.n_grads)


def resolve_iqeb_energy_tolerance(cfg: ExperimentConfig) -> float:
    return float(cfg.quantum.iqeb.energy_tolerance)


def resolve_quantum_algorithm_factory(cfg: ExperimentConfig) -> str | None:
    return cfg.quantum.algorithm_factory


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
        "shots_per_matrix_element": qse.shots_per_matrix_element,
        "shots_per_ij_term": qse.shots_per_ij_term,
    }


def resolve_qpe_demo_track_n_bits(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.demos.qpe.demo_track_n_bits)


def quantum_workflow_preview_vqs_fields(cfg: ExperimentConfig) -> dict[str, object]:
    v = cfg.quantum.demos.vqs
    return {
        "vqs_track_after_variational": v.track_after_variational,
        "vqs_pipeline_integration": v.pipeline_integration,
        "vqs_mode": v.mode,
        "vqs_n_times": v.n_times,
        "vqs_dt": float(v.dt),
    }


def quantum_workflow_preview_qpe_fields(cfg: ExperimentConfig) -> dict[str, object]:
    qpe = cfg.quantum.demos.qpe
    return {
        "qpe_demo_track_after_variational": qpe.track_after_variational,
        "qpe_pipeline_integration": qpe.pipeline_integration,
        "qpe_demo_track_n_bits": resolve_qpe_demo_track_n_bits(cfg),
    }


def quantum_variational_run_summary_yaml_fields(cfg: ExperimentConfig) -> dict[str, object]:
    """ADAPT / IQEB YAML keys copied into ``run_summary`` when bundles are present."""
    return {
        "adapt_pool_id_yaml": resolve_adapt_pool_id(cfg),
        "adapt_max_iter_yaml": resolve_adapt_max_iter(cfg),
        "iqeb_pool_id_yaml": resolve_iqeb_pool_id(cfg),
        "iqeb_max_rounds_yaml": resolve_iqeb_max_rounds(cfg),
    }


def quantum_algorithm_report_run_summary_fields(out: dict[str, object]) -> dict[str, object]:
    """Stable ``run_summary`` keys mirrored from pipeline ``algorithm_report``."""
    ar = out.get("algorithm_report")
    if not isinstance(ar, dict):
        return {}
    fields: dict[str, object] = {}
    schema = ar.get("schema")
    if isinstance(schema, str):
        fields["algorithm_report_schema"] = schema
    algorithm = ar.get("algorithm")
    if isinstance(algorithm, str):
        fields["algorithm_report_algorithm"] = algorithm
    nfev = ar.get("nfev")
    if isinstance(nfev, (int, float)):
        fields["algorithm_report_nfev"] = int(nfev)
    final_value = ar.get("final_value")
    if isinstance(final_value, (int, float)):
        fields["algorithm_report_final_value_au"] = float(final_value)
    return fields


def qpe_demo_track_requested(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.demos.qpe.track_requested())


def qpe_three_pack_requested(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.demos.qpe.three_pack_requested())


def vqs_track_requested(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.demos.vqs.track_requested())


def pauli_protocol_enabled(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.use_protocol)


def pauli_run_sampled(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.run_sampled)


def pauli_run_qiskit_shots(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.run_qiskit_shots)


def resolve_pauli_grouping(
    cfg: ExperimentConfig,
) -> Literal["tensor_product", "greedy_commuting"]:
    return cfg.quantum.pauli.grouping


def pauli_record_histograms(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.record_histograms)


def resolve_pauli_support_max_terms(cfg: ExperimentConfig) -> int | None:
    return cfg.quantum.pauli.support_max_terms


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


def tensornet_expectation_stub_enabled(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.tensornet.expectation_stub)


def resolve_tensornet_contraction_engine(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.tensornet.contraction_engine)


def resolve_vqs_track_payload_kwargs(cfg: ExperimentConfig) -> VqsTrackPayloadKwargs:
    v = cfg.quantum.demos.vqs
    return {
        "mode": v.mode,
        "n_times": v.n_times,
        "dt": float(v.dt),
        "rhs_mode_yaml": v.rhs_mode,
        "tangent_fd_epsilon_yaml": float(v.tangent_fd_epsilon),
    }


def quantum_demo_open_stack_yaml_flags(cfg: ExperimentConfig) -> dict[str, object]:
    """Demo-track YAML flags embedded in open-stack contract sidecars."""
    q = cfg.quantum
    return {
        "qpe_demo_track_after_variational": q.demos.qpe.track_after_variational,
        "qpe_pipeline_integration": q.demos.qpe.pipeline_integration,
        "vqs_track_after_variational": q.demos.vqs.track_after_variational,
        "vqs_pipeline_integration": q.demos.vqs.pipeline_integration,
        "vqs_rhs_mode_yaml": q.demos.vqs.rhs_mode,
        "vqs_tangent_fd_epsilon_yaml": float(q.demos.vqs.tangent_fd_epsilon),
        "vqs_mode_yaml": q.demos.vqs.mode,
    }


PAULI_PATH_DISABLED = "pauli_protocol_disabled"
PAULI_PATH_EXACT = "exact_executor"
PAULI_PATH_STATEVECTOR_SHOT_SIM = "statevector_grouped_shot_simulation"
PAULI_PATH_QISKIT_COUNTS = "qiskit_get_counts_bitstrings"


def classify_pauli_expectation_path_from_flags(
    *,
    use_protocol: bool,
    run_sampled: bool,
    run_qiskit_shots: bool,
) -> str:
    if not use_protocol:
        return PAULI_PATH_DISABLED
    if run_sampled and run_qiskit_shots:
        raise ValueError(
            "run_sampled_pauli_protocol and run_qiskit_shots_pauli_protocol are mutually exclusive"
        )
    if run_sampled:
        return PAULI_PATH_STATEVECTOR_SHOT_SIM
    if run_qiskit_shots:
        return PAULI_PATH_QISKIT_COUNTS
    return PAULI_PATH_EXACT


def classify_pauli_expectation_path_for_config(cfg: ExperimentConfig) -> str:
    return classify_pauli_expectation_path_from_flags(
        use_protocol=pauli_protocol_enabled(cfg),
        run_sampled=pauli_run_sampled(cfg),
        run_qiskit_shots=pauli_run_qiskit_shots(cfg),
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


def quantum_repro_core_fields(cfg: ExperimentConfig) -> dict[str, object]:
    """Stable repro snapshot keys derived from quantum + related config."""
    q = cfg.quantum
    out: dict[str, object] = {
        "quantum_algorithm": q.algorithm,
        "use_pauli_protocol": q.pauli.use_protocol,
        "vqe_depth": q.vqe.depth,
        "vqe_maxiter": q.vqe.maxiter,
        "adapt_max_iter": q.adapt.max_iter,
        "iqeb_max_rounds": q.iqeb.max_rounds,
        "variational_ansatz": q.variational.ansatz,
        "run_sampled_pauli_protocol": q.pauli.run_sampled,
        "run_qiskit_shots_pauli_protocol": q.pauli.run_qiskit_shots,
        "record_pauli_measurement_histograms": q.pauli.record_histograms,
        "pauli_grouping": q.pauli.grouping,
        "pauli_support_max_terms": q.pauli.support_max_terms,
        "vqd_after_variational": q.excited.vqd.after_variational,
        "qse_after_variational": q.excited.qse.after_variational,
        "sceom_after_variational": q.excited.sceom.after_variational,
    }
    if q.algorithm_factory:
        out["quantum_algorithm_factory"] = q.algorithm_factory
    if q.variational.ansatz == "uccsd" and q.variational.uccsd_trotter_steps is not None:
        out["uccsd_trotter_steps"] = q.variational.uccsd_trotter_steps
    return out


def quantum_repro_sidecar_fields(cfg: ExperimentConfig) -> dict[str, object]:
    """Detailed excited-state, demo-track, and tensornet YAML keys for parity snapshots."""
    q = cfg.quantum
    return {
        "vqd_overlap_exponent_yaml": float(q.excited.vqd.overlap_exponent),
        "vqd_cobyla_maxiter_yaml": int(q.excited.vqd.cobyla_maxiter),
        "vqd_n_states": q.excited.vqd.n_states,
        "vqd_penalty_weight": q.excited.vqd.penalty_weight,
        "vqd_penalty_weights": q.excited.vqd.penalty_weights,
        "vqd_optimizer_method_yaml": q.excited.vqd.optimizer_method,
        "vqd_init_strategy_yaml": q.excited.vqd.init_strategy,
        "vqd_init_noise_scale_yaml": float(q.excited.vqd.init_noise_scale),
        "vqd_max_overlap_warn_yaml": q.excited.vqd.max_overlap_warn,
        "vqd_overlap_mode_yaml": q.excited.vqd.overlap_mode,
        "vqd_shots_objective": q.excited.vqd.shots_objective,
        "vqd_shots_overlap": q.excited.vqd.shots_overlap,
        "vqd_shots_weight": q.excited.vqd.shots_weight,
        "qse_subspace_dim": q.excited.qse.subspace_dim,
        "qse_max_basis": q.excited.qse.max_basis,
        "qse_shot_mode": q.excited.qse.shot_mode,
        "qse_shots_per_matrix_element": q.excited.qse.shots_per_matrix_element,
        "qse_shots_per_ij_term": q.excited.qse.shots_per_ij_term,
        "sceom_subspace_dim": q.excited.sceom.subspace_dim,
        "sceom_shots_per_matrix_element": q.excited.sceom.shots_per_matrix_element,
        "sceom_generator_strategy_yaml": q.excited.sceom.generator_strategy,
        "vqs_track_after_variational": q.demos.vqs.track_after_variational,
        "vqs_pipeline_integration": q.demos.vqs.pipeline_integration,
        "vqs_mode": q.demos.vqs.mode,
        "vqs_n_times": q.demos.vqs.n_times,
        "vqs_dt": float(q.demos.vqs.dt),
        "vqs_rhs_mode_yaml": q.demos.vqs.rhs_mode,
        "vqs_tangent_fd_epsilon_yaml": float(q.demos.vqs.tangent_fd_epsilon),
        "qpe_demo_track_after_variational_yaml": q.demos.qpe.track_after_variational,
        "qpe_pipeline_integration_yaml": q.demos.qpe.pipeline_integration,
        "qpe_demo_track_n_bits_yaml": int(q.demos.qpe.demo_track_n_bits),
        "qpe_three_pack_after_variational_yaml": q.demos.qpe.three_pack.after_variational,
        "qpe_three_pack_time_yaml": float(q.demos.qpe.three_pack.time),
        "tensornet_expectation_stub": bool(q.tensornet.expectation_stub),
        "tensornet_contraction_engine": q.tensornet.contraction_engine,
    }

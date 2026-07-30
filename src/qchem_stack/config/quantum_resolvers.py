"""Variational, demo-track, and repro snapshot config resolvers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .experiment import ExperimentConfig
    from .quantum_excited_params import VqsTrackPayloadKwargs


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


def resolve_vsqs_intervals(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.variational.vsqs_intervals)


def resolve_vsqs_time(cfg: ExperimentConfig) -> float:
    return float(cfg.quantum.variational.vsqs_time)


def resolve_vsqs_trotter_order(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.variational.vsqs_trotter_order)


def resolve_uccsd_decomposition_mode(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.uccsd.decomposition_mode)


def resolve_vqe_optimizer_method(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.vqe.optimizer_method)


def resolve_vqe_initial_parameters_strategy(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.vqe.initial_parameters_strategy)


def resolve_adapt_max_iter(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.adapt.max_iter)


def resolve_adapt_pool_id(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.adapt.pool_id)


def resolve_adapt_grad_tol(cfg: ExperimentConfig) -> float:
    return float(cfg.quantum.adapt.grad_tol)


def resolve_iqeb_max_rounds(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.iqeb.max_rounds)


def resolve_iqeb_pool_id(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.iqeb.pool_id)


def resolve_iqeb_n_grads(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.iqeb.n_grads)


def resolve_iqeb_energy_tolerance(cfg: ExperimentConfig) -> float:
    return float(cfg.quantum.iqeb.energy_tolerance)


def resolve_iqcc_max_steps(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.iqcc.max_steps)


def resolve_iqcc_top_k(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.iqcc.top_k)


def resolve_iqcc_coeff_atol(cfg: ExperimentConfig) -> float:
    return float(cfg.quantum.iqcc.coeff_atol)


def resolve_iqcc_max_terms(cfg: ExperimentConfig) -> int | None:
    return cfg.quantum.iqcc.max_terms


def resolve_iqcc_enable_pt(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.iqcc.enable_pt)


def resolve_iqcc_denom_cutoff(cfg: ExperimentConfig) -> float:
    return float(cfg.quantum.iqcc.denom_cutoff)


def resolve_iqcc_pool_mode(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.iqcc.pool_mode)


def resolve_iqcc_pool_id(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.iqcc.pool_id)


def resolve_iqcc_max_weight(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.iqcc.max_weight)


def resolve_iqcc_energy_tolerance(cfg: ExperimentConfig) -> float:
    return float(cfg.quantum.iqcc.energy_tolerance)


def resolve_quantum_algorithm_factory(cfg: ExperimentConfig) -> str | None:
    return cfg.quantum.algorithm_factory


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
    """ADAPT / IQEB / iQCC YAML keys copied into ``run_summary`` when bundles are present."""
    return {
        "adapt_pool_id_yaml": resolve_adapt_pool_id(cfg),
        "adapt_max_iter_yaml": resolve_adapt_max_iter(cfg),
        "adapt_grad_tol_yaml": resolve_adapt_grad_tol(cfg),
        "iqeb_pool_id_yaml": resolve_iqeb_pool_id(cfg),
        "iqeb_max_rounds_yaml": resolve_iqeb_max_rounds(cfg),
        "iqcc_max_steps_yaml": resolve_iqcc_max_steps(cfg),
        "iqcc_top_k_yaml": resolve_iqcc_top_k(cfg),
        "iqcc_enable_pt_yaml": resolve_iqcc_enable_pt(cfg),
        "iqcc_pool_mode_yaml": resolve_iqcc_pool_mode(cfg),
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
        "iqcc_max_steps": q.iqcc.max_steps,
        "iqcc_top_k": q.iqcc.top_k,
        "iqcc_enable_pt": q.iqcc.enable_pt,
        "iqcc_pool_mode": q.iqcc.pool_mode,
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

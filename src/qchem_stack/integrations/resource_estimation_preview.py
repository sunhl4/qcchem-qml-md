"""Optional P2-W1 export hook: shallow resource / Methods narrative without cloud pricing."""

from __future__ import annotations

from typing import Any

from qchem_stack.config import ExperimentConfig
from qchem_stack.protocols.product_contract import pauli_protocol_expectation_path_for_config


def _attach_classical_benchmark_preview_alignment(
    base: dict[str, Any],
    pipeline_row: dict[str, Any],
    rsum: dict[str, Any],
) -> None:
    """Mirror ``methods_resource_unified`` classical digest fields (pipeline ``--results`` only)."""
    cbs_row = pipeline_row.get("classical_benchmark_summary")
    cbs_d: dict[str, Any] = cbs_row if isinstance(cbs_row, dict) else {}
    classical_active = bool(cbs_d.get("schema")) or (
        rsum.get("classical_benchmark_summary_present") is True
    )
    rec_method = cbs_d.get("recommended_baseline_method")
    rec_energy = cbs_d.get("recommended_baseline_energy_au")
    rec_policy = cbs_d.get("recommended_baseline_policy")
    sum_schema = cbs_d.get("schema")
    best_m = cbs_d.get("best_method")
    best_e = cbs_d.get("best_energy_au")
    if sum_schema is None:
        sum_schema = rsum.get("classical_benchmark_summary_schema")
    if rec_method is None:
        rec_method = rsum.get("classical_benchmark_recommended_baseline_method")
    if rec_energy is None:
        x = rsum.get("classical_benchmark_recommended_baseline_energy_au")
        rec_energy = float(x) if x is not None else None
    if best_m is None:
        best_m = rsum.get("classical_benchmark_best_method")
    if best_e is None:
        y = rsum.get("classical_benchmark_best_energy_au")
        best_e = float(y) if y is not None else None

    base["classical_benchmark_active"] = classical_active
    base["classical_benchmark_summary_schema"] = sum_schema
    base["classical_benchmark_recommended_baseline_policy"] = rec_policy
    base["classical_benchmark_recommended_baseline_method"] = rec_method
    base["classical_benchmark_recommended_baseline_energy_au"] = rec_energy
    base["classical_benchmark_best_method"] = best_m
    base["classical_benchmark_best_energy_au"] = best_e


def build_resource_estimation_preview_v1(
    *,
    cfg: ExperimentConfig,
    pipeline_row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Machine-readable **preview** slice for export parity (not a full resource estimator).

    When ``pipeline_row`` is present (``export_parity_criteria_table --results``), merge a small
    pick-list from ``resource_summary``; otherwise emit a config-scoped stub.

    Classical benchmark mirrors share semantics with ``build_methods_resource_unified_v1`` so both
    exports stay comparable on Methods-facing tables.
    """
    pi = cfg.parity_integrations
    qt = cfg.quantum
    act = cfg.active_space
    mit = cfg.mitigation
    be = cfg.backend
    ce = cfg.chemistry_extended
    base: dict[str, Any] = {
        "schema": "resource_estimation_preview_v1",
        "mode": "pipeline" if pipeline_row else "config_only",
        "epistemic_bound": (
            "Open-stack preview only: no HQC/Nexus currency, no vendor L0 resource guarantee."
        ),
        "quantum_algorithm_yaml": qt.algorithm,
        "algorithm_factory_yaml": qt.algorithm_factory,
        "adapt_pool_id_yaml": qt.adapt_pool_id,
        "iqeb_pool_id_yaml": qt.iqeb_pool_id,
        "variational_ansatz_yaml": qt.variational_ansatz,
        "fermion_qubit_mapping_yaml": act.fermion_qubit_mapping,
        "backend_provider_yaml": be.provider,
        "zne_enabled_yaml": mit.zne_enabled,
        "mitigation_zne_mode_yaml": mit.zne_mode,
        "mitigation_zne_scales_yaml": [float(x) for x in mit.zne_scales],
        "pmsv_enabled_yaml": mit.pmsv_enabled,
        "run_sampled_pauli_protocol_yaml": qt.run_sampled_pauli_protocol,
        "run_qiskit_shots_pauli_protocol_yaml": qt.run_qiskit_shots_pauli_protocol,
        "pauli_protocol_expectation_path_yaml": pauli_protocol_expectation_path_for_config(cfg),
        "classical_benchmark_enabled_yaml": ce.classical_benchmark_enabled,
        "qpe_demo_track_after_variational": qt.qpe_demo_track_after_variational,
        "qpe_pipeline_integration": qt.qpe_pipeline_integration,
        "qpe_demo_track_n_bits": int(qt.qpe_demo_track_n_bits),
        "qpe_three_pack_after_variational": qt.qpe_three_pack_after_variational,
        "qpe_three_pack_time_yaml": float(qt.qpe_three_pack_time),
        "qpe_three_pack_deterministic_rounds_yaml": int(qt.qpe_three_pack_deterministic_rounds),
        "qpe_three_pack_kitaev_bits_yaml": int(qt.qpe_three_pack_kitaev_bits),
        "qpe_three_pack_info_samples_yaml": int(qt.qpe_three_pack_info_samples),
        "vqs_track_after_variational": qt.vqs_track_after_variational,
        "vqs_pipeline_integration": qt.vqs_pipeline_integration,
        "vqs_mode_yaml": qt.vqs_mode,
        "vqs_n_times_yaml": int(qt.vqs_n_times),
        "vqs_dt_yaml": float(qt.vqs_dt),
        "vqs_rhs_mode_yaml": qt.vqs_rhs_mode,
        "vqs_tangent_fd_epsilon_yaml_preview": float(qt.vqs_tangent_fd_epsilon),
        "vqd_overlap_exponent_yaml": float(qt.vqd_overlap_exponent),
        "vqd_cobyla_maxiter_yaml": int(qt.vqd_cobyla_maxiter),
        "vqd_overlap_mode_yaml": qt.vqd_overlap_mode,
        "vqd_optimizer_method_yaml": qt.vqd_optimizer_method,
        "vqd_init_strategy_yaml": qt.vqd_init_strategy,
        "vqd_init_noise_scale_yaml": float(qt.vqd_init_noise_scale),
        "vqd_max_overlap_warn_yaml": qt.vqd_max_overlap_warn,
        "sceom_generator_strategy_yaml": qt.sceom_generator_strategy,
        "parity_integrations_tket_first_circuit_stats": pi.tket_first_circuit_stats,
        "use_pauli_protocol": qt.use_pauli_protocol,
        "spam_calibration_enabled_yaml": mit.spam_calibration_enabled,
        "classical_shadows_stub_enabled_yaml": mit.classical_shadows_stub_enabled,
        "classical_shadows_budget_pairs_yaml": int(mit.classical_shadows_budget_pairs),
    }
    if not pipeline_row:
        return base
    rs = pipeline_row.get("resource_summary")
    if isinstance(rs, dict):
        for k in (
            "n_circuits",
            "n_qubits",
            "sum_shots",
            "max_depth",
            "sum_twoq",
            "n_pauli_terms",
            "n_pauli_groups",
            "pauli_averaging_protocol_ran",
            "excited_shots_upper_bound",
            "sum_shots_total_with_excited_upper_bound",
        ):
            if k in rs and rs[k] is not None:
                base[f"resource_summary_{k}"] = rs[k]
    rsum: dict[str, Any] = {}
    repro = pipeline_row.get("repro")
    if isinstance(repro, dict):
        raw_rs = repro.get("run_summary")
        if isinstance(raw_rs, dict):
            rsum = raw_rs
        for k in (
            "protocol_total_shots_budget",
            "protocol_n_measurement_circuits",
            "protocol_shots_per_circuit_effective",
            "protocol_energy_stderr",
            "protocol_expectation_source",
            "protocol_energy_stderr_model",
            "protocol_zne_mode",
            "excited_shots_upper_bound",
            "sum_shots_total_with_excited_upper_bound",
            "pauli_averaging_protocol_ran",
        ):
            if k in rsum and rsum[k] is not None:
                base[f"run_summary_{k}"] = rsum[k]
        if rsum.get("qpe_three_pack_ran") is True:
            base["run_summary_qpe_three_pack_ran"] = True
        triple = (
            (
                "qpe_three_pack_deterministic_energy_est",
                "qpe_three_pack_deterministic_energy_est_from_run",
            ),
            ("qpe_three_pack_kitaev_energy_est", "qpe_three_pack_kitaev_energy_est_from_run"),
            (
                "qpe_three_pack_info_theory_energy_est",
                "qpe_three_pack_info_theory_energy_est_from_run",
            ),
        )
        for src_k, dst_k in triple:
            val = rsum.get(src_k)
            if val is not None:
                base[dst_k] = val
        ps = repro.get("parity_snapshot")
        if isinstance(ps, dict):
            if ps.get("mitigation_zne_scales") is not None:
                base["parity_snapshot_mitigation_zne_scales"] = [
                    float(x) for x in ps["mitigation_zne_scales"]
                ]
            if ps.get("mitigation_zne_mode") is not None:
                base["parity_snapshot_mitigation_zne_mode"] = ps["mitigation_zne_mode"]
    _attach_classical_benchmark_preview_alignment(base, pipeline_row, rsum)
    return base

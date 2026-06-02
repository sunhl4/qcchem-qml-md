"""Optional P2-W1 export hook: shallow resource / Methods narrative without cloud pricing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import RESOURCE_ESTIMATION_PREVIEW_V1
from qchem_stack.protocols.product_contract import pauli_protocol_expectation_path_for_config

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


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
        "schema": RESOURCE_ESTIMATION_PREVIEW_V1,
        "mode": "pipeline" if pipeline_row else "config_only",
        "epistemic_bound": (
            "Open-stack preview only: no HQC/Nexus currency, no vendor L0 resource guarantee."
        ),
        "quantum_algorithm_yaml": qt.algorithm,
        "algorithm_factory_yaml": qt.algorithm_factory,
        "adapt_pool_id_yaml": qt.adapt.pool_id,
        "iqeb_pool_id_yaml": qt.iqeb.pool_id,
        "variational_ansatz_yaml": qt.variational.ansatz,
        "fermion_qubit_mapping_yaml": act.mapping.fermion_qubit,
        "backend_provider_yaml": be.provider,
        "zne_enabled_yaml": mit.zne.enabled,
        "mitigation_zne_mode_yaml": mit.zne.mode,
        "mitigation_zne_scales_yaml": [float(x) for x in mit.zne.scales],
        "pmsv_enabled_yaml": mit.pmsv.enabled,
        "run_sampled_pauli_protocol_yaml": qt.pauli.run_sampled,
        "run_qiskit_shots_pauli_protocol_yaml": qt.pauli.run_qiskit_shots,
        "pauli_protocol_expectation_path_yaml": pauli_protocol_expectation_path_for_config(cfg),
        "classical_benchmark_enabled_yaml": ce.benchmarks.enabled,
        "qpe_demo_track_after_variational": qt.demos.qpe.track_after_variational,
        "qpe_pipeline_integration": qt.demos.qpe.pipeline_integration,
        "qpe_demo_track_n_bits": int(qt.demos.qpe.demo_track_n_bits),
        "qpe_three_pack_after_variational": qt.demos.qpe.three_pack.after_variational,
        "qpe_three_pack_time_yaml": float(qt.demos.qpe.three_pack.time),
        "qpe_three_pack_deterministic_rounds_yaml": int(
            qt.demos.qpe.three_pack.deterministic_rounds
        ),
        "qpe_three_pack_kitaev_bits_yaml": int(qt.demos.qpe.three_pack.kitaev_bits),
        "qpe_three_pack_info_samples_yaml": int(qt.demos.qpe.three_pack.info_samples),
        "vqs_track_after_variational": qt.demos.vqs.track_after_variational,
        "vqs_pipeline_integration": qt.demos.vqs.pipeline_integration,
        "vqs_mode_yaml": qt.demos.vqs.mode,
        "vqs_n_times_yaml": int(qt.demos.vqs.n_times),
        "vqs_dt_yaml": float(qt.demos.vqs.dt),
        "vqs_rhs_mode_yaml": qt.demos.vqs.rhs_mode,
        "vqs_tangent_fd_epsilon_yaml_preview": float(qt.demos.vqs.tangent_fd_epsilon),
        "vqd_overlap_exponent_yaml": float(qt.excited.vqd.overlap_exponent),
        "vqd_cobyla_maxiter_yaml": int(qt.excited.vqd.cobyla_maxiter),
        "vqd_overlap_mode_yaml": qt.excited.vqd.overlap_mode,
        "vqd_optimizer_method_yaml": qt.excited.vqd.optimizer_method,
        "vqd_init_strategy_yaml": qt.excited.vqd.init_strategy,
        "vqd_init_noise_scale_yaml": float(qt.excited.vqd.init_noise_scale),
        "vqd_max_overlap_warn_yaml": qt.excited.vqd.max_overlap_warn,
        "sceom_generator_strategy_yaml": qt.excited.sceom.generator_strategy,
        "parity_integrations_tket_first_circuit_stats": pi.tket_first_circuit_stats,
        "ft_resource_depth_formula_v1": "sum_twoq * native_twoq_weight + n_pauli_groups",
        "ft_t_gate_proxy_formula_v1": "n_pauli_rotations * log2(1/epsilon)",
        "use_pauli_protocol": qt.pauli.use_protocol,
        "spam_calibration_enabled_yaml": mit.stubs.spam_calibration,
        "classical_shadows_stub_enabled_yaml": mit.stubs.classical_shadows,
        "classical_shadows_budget_pairs_yaml": int(mit.stubs.classical_shadows_budget_pairs),
        "compiler_pass_bundle_yaml": list(cfg.compiler.compiler_passes),
        "compiler_preoptimize_passes_yaml": list(cfg.compiler.preoptimize_passes),
        "tket_probe_requested": pi.tket_first_circuit_stats,
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
        if rs.get("max_depth") is not None:
            base["ft_circuit_depth_estimate"] = rs["max_depth"]
        if rs.get("n_qubits") is not None:
            base["ft_circuit_width_estimate"] = rs["n_qubits"]
        max_depth = rs.get("max_depth")
        sum_twoq = rs.get("sum_twoq")
        if max_depth is not None:
            twoq = int(sum_twoq) if sum_twoq is not None else 0
            base["ft_two_qubit_depth_proxy"] = int(max_depth) * max(1, twoq)
        if rs.get("n_pauli_groups") is not None:
            base["ft_measurement_rounds_proxy"] = int(rs["n_pauli_groups"])
        excited_acct = rs.get("excited_shot_accounting")
        if isinstance(excited_acct, dict) and excited_acct:
            base["excited_shot_budget_breakdown"] = dict(excited_acct)
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

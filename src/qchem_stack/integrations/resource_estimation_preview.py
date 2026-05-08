"""Optional P2-W1 export hook: shallow resource / Methods narrative without cloud pricing."""

from __future__ import annotations

from typing import Any

from qchem_stack.config import ExperimentConfig


def build_resource_estimation_preview_v1(
    *,
    cfg: ExperimentConfig,
    pipeline_row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Machine-readable **preview** slice for export parity (not a full resource estimator).

    When ``pipeline_row`` is present (``export_parity_criteria_table --results``), merge a small
    pick-list from ``resource_summary``; otherwise emit a config-scoped stub.
    """
    pi = cfg.parity_integrations
    qt = cfg.quantum
    base: dict[str, Any] = {
        "schema": "resource_estimation_preview_v1",
        "mode": "pipeline" if pipeline_row else "config_only",
        "epistemic_bound": (
            "Open-stack preview only: no HQC/Nexus currency, no vendor L0 resource guarantee."
        ),
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
        "sceom_generator_strategy_yaml": qt.sceom_generator_strategy,
        "parity_integrations_tket_first_circuit_stats": pi.tket_first_circuit_stats,
        "use_pauli_protocol": qt.use_pauli_protocol,
        "spam_calibration_enabled_yaml": cfg.mitigation.spam_calibration_enabled,
        "classical_shadows_stub_enabled_yaml": cfg.mitigation.classical_shadows_stub_enabled,
        "classical_shadows_budget_pairs_yaml": int(cfg.mitigation.classical_shadows_budget_pairs),
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
        ):
            if k in rs and rs[k] is not None:
                base[f"resource_summary_{k}"] = rs[k]
    repro = pipeline_row.get("repro")
    if isinstance(repro, dict):
        rsum = repro.get("run_summary") if isinstance(repro.get("run_summary"), dict) else {}
        if rsum.get("qpe_three_pack_ran") is True:
            base["run_summary_qpe_three_pack_ran"] = True
        triple = (
            ("qpe_three_pack_deterministic_energy_est", "qpe_three_pack_deterministic_energy_est_from_run"),
            ("qpe_three_pack_kitaev_energy_est", "qpe_three_pack_kitaev_energy_est_from_run"),
            ("qpe_three_pack_info_theory_energy_est", "qpe_three_pack_info_theory_energy_est_from_run"),
        )
        for src_k, dst_k in triple:
            val = rsum.get(src_k)
            if val is not None:
                base[dst_k] = val
    return base

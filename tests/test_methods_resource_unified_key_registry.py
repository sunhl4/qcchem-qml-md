"""Top-level keys on ``methods_resource_unified_v1`` must stay registered."""

from __future__ import annotations

from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]


def test_methods_resource_unified_v1_top_level_keys_registered() -> None:
    from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1
    from qchem_stack.internal_reports.competitor.inquanto_contract import (
        METHODS_RESOURCE_UNIFIED_V1_DOCUMENTED_KEYS,
    )

    row = {
        "resource_summary": {
            "n_circuits": 1,
            "pauli_averaging_protocol_ran": True,
            "excited_shots_upper_bound": 2,
            "sum_shots_total_with_excited_upper_bound": 3,
        },
        "repro": {
            "parity_snapshot": {},
            "run_summary": {
                "classical_backend_id": "pyscf",
                "quantum_algorithm_yaml": "vqe",
                "protocol_total_shots_budget": 100,
                "protocol_expectation_source": "exact_executor",
                "excited_shots_upper_bound": 2,
            },
        },
    }
    uni = build_methods_resource_unified_v1(row)
    unknown = set(uni.keys()) - METHODS_RESOURCE_UNIFIED_V1_DOCUMENTED_KEYS
    assert not unknown, sorted(unknown)


@pytest.mark.skipif(
    not (_ROOT / "configs" / "example_h2_qpe_track_parity_integrations.yaml").is_file(),
    reason="config missing",
)
def test_methods_resource_unified_matches_preview_protocol_mirror_after_pipeline() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("pytket")

    from qchem_stack.config import load_experiment_config
    from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1
    from qchem_stack.integrations.resource_estimation_preview import (
        build_resource_estimation_preview_v1,
    )
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = _ROOT / "configs" / "example_h2_qpe_track_parity_integrations.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    uni = build_methods_resource_unified_v1(out)
    rev = build_resource_estimation_preview_v1(cfg=cfg, pipeline_row=out)

    overlap = (
        "run_summary_protocol_total_shots_budget",
        "run_summary_protocol_n_measurement_circuits",
        "run_summary_protocol_shots_per_circuit_effective",
        "run_summary_protocol_energy_stderr",
        "run_summary_protocol_expectation_source",
        "run_summary_protocol_energy_stderr_model",
        "run_summary_protocol_zne_mode",
        "run_summary_excited_shots_upper_bound",
        "run_summary_sum_shots_total_with_excited_upper_bound",
        "run_summary_pauli_averaging_protocol_ran",
        "classical_benchmark_active",
        "classical_benchmark_summary_schema",
        "classical_benchmark_recommended_baseline_policy",
        "classical_benchmark_recommended_baseline_method",
        "classical_benchmark_recommended_baseline_energy_au",
        "classical_benchmark_best_method",
        "classical_benchmark_best_energy_au",
    )
    for k in overlap:
        if k in rev and k in uni:
            assert uni[k] == rev[k], k

    for zk in ("mitigation_zne_mode_yaml", "mitigation_zne_scales_yaml"):
        assert uni.get(zk) == rev.get(zk), zk


@pytest.mark.skipif(
    not (_ROOT / "configs" / "example_h2_zne_circuit_fold.yaml").is_file(),
    reason="config missing",
)
def test_preview_unified_zne_yaml_matches_after_pipeline() -> None:
    pytest.importorskip("pyscf")

    from qchem_stack.config import load_experiment_config
    from qchem_stack.integrations.methods_resource_unified import build_methods_resource_unified_v1
    from qchem_stack.integrations.resource_estimation_preview import (
        build_resource_estimation_preview_v1,
    )
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = _ROOT / "configs" / "example_h2_zne_circuit_fold.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    uni = build_methods_resource_unified_v1(out)
    rev = build_resource_estimation_preview_v1(cfg=cfg, pipeline_row=out)
    assert uni.get("mitigation_zne_mode_yaml") == rev.get("mitigation_zne_mode_yaml")
    assert uni.get("mitigation_zne_scales_yaml") == rev.get("mitigation_zne_scales_yaml")
    assert rev.get("mitigation_zne_mode_yaml") == "circuit_scale_fold"
    assert rev.get("mitigation_zne_scales_yaml") == [1.0, 2.0, 3.0]
    snap = out.get("repro", {}).get("parity_snapshot") if isinstance(out.get("repro"), dict) else {}
    assert isinstance(snap, dict)
    assert rev.get("parity_snapshot_mitigation_zne_scales") == [1.0, 2.0, 3.0]
    assert rev.get("parity_snapshot_mitigation_zne_mode") == "circuit_scale_fold"

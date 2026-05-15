"""``resource_estimation_preview_v1`` export keys must stay registered (P2-W1)."""

from __future__ import annotations

from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]


def test_resource_estimation_preview_keys_subset_of_contract_registry() -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.integrations.resource_estimation_preview import (
        build_resource_estimation_preview_v1,
    )
    from qchem_stack.internal_reports.competitor.inquanto_contract import (
        RESOURCE_ESTIMATION_PREVIEW_V1_DOCUMENTED_KEYS,
    )

    cfg_path = _ROOT / "configs" / "example_h2_qpe_track_parity_integrations.yaml"
    if not cfg_path.is_file():
        pytest.skip("configs/example_h2_qpe_track_parity_integrations.yaml missing")
    cfg = load_experiment_config(cfg_path)

    d0 = build_resource_estimation_preview_v1(cfg=cfg)
    unknown = set(d0.keys()) - RESOURCE_ESTIMATION_PREVIEW_V1_DOCUMENTED_KEYS
    assert not unknown, sorted(unknown)

    row = {
        "resource_summary": {
            "n_circuits": 1,
            "n_qubits": 2,
            "sum_shots": 3,
            "max_depth": 4,
            "sum_twoq": 5,
            "n_pauli_terms": 6,
            "n_pauli_groups": 7,
            "pauli_averaging_protocol_ran": False,
            "excited_shots_upper_bound": 8,
            "sum_shots_total_with_excited_upper_bound": 9,
        },
        "classical_benchmark_summary": {
            "schema": "classical_benchmark_summary_v1",
            "recommended_baseline_policy": "prefer_ccsd_else_mp2_else_hf",
            "recommended_baseline_method": "ccsd",
            "recommended_baseline_energy_au": -1.1,
            "best_method": "ccsd",
            "best_energy_au": -1.1,
        },
        "repro": {
            "parity_snapshot": {
                "mitigation_zne_scales": [1.0, 2.0],
                "mitigation_zne_mode": "scalar_stub",
            },
            "run_summary": {
                "protocol_total_shots_budget": 10,
                "protocol_n_measurement_circuits": 11,
                "protocol_shots_per_circuit_effective": 12.0,
                "protocol_energy_stderr": 0.01,
                "protocol_expectation_source": "x",
                "protocol_energy_stderr_model": "y",
                "protocol_zne_mode": None,
                "excited_shots_upper_bound": 13,
                "sum_shots_total_with_excited_upper_bound": 14,
                "pauli_averaging_protocol_ran": True,
                "qpe_three_pack_ran": True,
                "qpe_three_pack_deterministic_energy_est": -1.0,
                "qpe_three_pack_kitaev_energy_est": -2.0,
                "qpe_three_pack_info_theory_energy_est": -3.0,
            },
        },
    }
    d1 = build_resource_estimation_preview_v1(cfg=cfg, pipeline_row=row)
    unknown1 = set(d1.keys()) - RESOURCE_ESTIMATION_PREVIEW_V1_DOCUMENTED_KEYS
    assert not unknown1, sorted(unknown1)

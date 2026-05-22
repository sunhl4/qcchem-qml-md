"""Excited-stage shot upper bounds merged into resource_summary (no PySCF)."""

from __future__ import annotations

from qchem_stack.orchestration.excited_stages import (
    excited_shot_channel_upper_bounds,
    excited_shots_upper_bound,
)
from qchem_stack.orchestration.protocol_finalize_resource import resource_summary_excited_only


def test_excited_shots_upper_bound_vqd_qse_sceom() -> None:
    ex: dict = {
        "vqd": {
            "swap_test_pair_count_if_shots": 3,
            "shots_overlap_per_pair": 10,
            "deflated_cobyla_levels": 2,
            "shots_objective_per_reporting_level": 5,
            "shots_weight_channel": 2,
        },
        "qse": {"total_shots_upper_bound": 1000},
        "sceom": {"m_matrix_elements": 4, "shots_per_matrix_element_yaml": 25},
    }
    # VQD: 3*10 + 2*5 + 2*2 (weight with overlap>0) = 44; QSE: 1000; SCEOM: 100
    assert excited_shots_upper_bound(ex) == 1144


def test_excited_shots_upper_bound_gaussian_h_fallback() -> None:
    ex = {"qse": {"gaussian_h_shots_budget_reference": 64}}
    assert excited_shots_upper_bound(ex) == 64


def test_excited_shots_upper_bound_qse_pauli_tasks_times_shots_fallback() -> None:
    ex = {"qse": {"n_transition_tasks": 10, "shots_per_ij_term_yaml": 32}}
    assert excited_shots_upper_bound(ex) == 320


def test_excited_shots_upper_bound_qse_prefers_schedule_over_task_fallback() -> None:
    ex = {
        "qse": {
            "total_shots_upper_bound": 100,
            "n_transition_tasks": 10,
            "shots_per_ij_term_yaml": 32,
        }
    }
    assert excited_shots_upper_bound(ex) == 100


def test_resource_summary_excited_only_shape() -> None:
    er = {
        "vqd": {"n_states": 2, "deflated_cobyla_levels": 0},
        "shot_channel_upper_bounds": {"vqd": 0, "qse": 0, "sceom": 0, "combined": 0},
    }
    rs = resource_summary_excited_only(2, er)
    assert rs["n_circuits"] == 0
    assert rs["pauli_averaging_protocol_ran"] is False
    assert rs["excited_stages"] is er
    assert rs["sum_shots_total_with_excited_upper_bound"] == rs["excited_shots_upper_bound"]
    assert rs["excited_shot_accounting"]["combined"] == 0


def test_excited_shot_channel_upper_bounds_table() -> None:
    ex = {
        "vqd": {
            "swap_test_pair_count_if_shots": 1,
            "shots_overlap_per_pair": 8,
            "deflated_cobyla_levels": 1,
            "shots_objective_per_reporting_level": 4,
            "shots_weight_channel": 0,
        },
        "qse": {"total_shots_upper_bound": 50},
    }
    b = excited_shot_channel_upper_bounds(ex)
    assert b["vqd"] == 8 + 4
    assert b["qse"] == 50
    assert b["sceom"] == 0
    assert b["combined"] == b["vqd"] + b["qse"] + b["sceom"]

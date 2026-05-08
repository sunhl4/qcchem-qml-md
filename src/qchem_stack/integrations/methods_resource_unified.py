"""Unified Methods-facing resource slice for export (QPE track + variational + TKET probe)."""

from __future__ import annotations

from typing import Any


def build_methods_resource_unified_v1(pipeline_row: dict[str, Any]) -> dict[str, Any]:
    """
    Merge ``resource_summary``, optional ``qpe_demo_track``, parity TKET probe, and optional
    classical benchmark summary (when ``chemistry_extended.classical_benchmark_enabled``) into one blob.

    Intended for ``export_parity_criteria_table.py --results`` parity with plain VQE YAML exports.
    """
    rs = pipeline_row.get("resource_summary") if isinstance(pipeline_row.get("resource_summary"), dict) else {}
    qpe = pipeline_row.get("qpe_demo_track") if isinstance(pipeline_row.get("qpe_demo_track"), dict) else None
    repro = pipeline_row.get("repro") if isinstance(pipeline_row.get("repro"), dict) else {}
    ps = repro.get("parity_snapshot") if isinstance(repro.get("parity_snapshot"), dict) else {}
    tket = ps.get("tket_first_compiled_circuit_probe")
    rsum = repro.get("run_summary") if isinstance(repro.get("run_summary"), dict) else {}

    rs_pick = {
        k: rs[k]
        for k in (
            "n_circuits",
            "n_qubits",
            "sum_shots",
            "max_depth",
            "sum_twoq",
            "pauli_averaging_protocol_ran",
            "n_pauli_terms",
            "n_pauli_groups",
        )
        if k in rs and rs[k] is not None
    }
    qpe_compact: dict[str, Any] | None = None
    if isinstance(qpe, dict):
        pec = qpe.get("phase_estimation_contract_v1")
        pec_d = pec if isinstance(pec, dict) else None
        qpe_compact = {
            "schema": qpe.get("schema"),
            "has_kitaev_dense": qpe.get("kitaev_ground_energy_dense") is not None,
            "has_bayesian_stub": qpe.get("bayesian_phase_map_toy") is not None,
            "phase_estimation_contract_schema": pec_d.get("schema") if pec_d else None,
        }

    tket_schema = tket.get("schema") if isinstance(tket, dict) else None

    cbs = pipeline_row.get("classical_benchmark_summary")
    cbs_d: dict[str, Any] = cbs if isinstance(cbs, dict) else {}
    classical_active = bool(cbs_d.get("schema")) or (
        isinstance(rsum, dict) and rsum.get("classical_benchmark_summary_present") is True
    )
    rec_method = cbs_d.get("recommended_baseline_method")
    rec_energy = cbs_d.get("recommended_baseline_energy_au")
    rec_policy = cbs_d.get("recommended_baseline_policy")
    sum_schema = cbs_d.get("schema")
    best_m = cbs_d.get("best_method")
    best_e = cbs_d.get("best_energy_au")
    if isinstance(rsum, dict):
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

    qpe_contract = rsum.get("qpe_open_stack_contract_v1")
    qpe_contract_d: dict[str, Any] | None = qpe_contract if isinstance(qpe_contract, dict) else None
    vqs_contract = rsum.get("vqs_open_stack_contract_v1")
    vqs_contract_d: dict[str, Any] | None = vqs_contract if isinstance(vqs_contract, dict) else None

    ers = pipeline_row.get("excited_resource_summary")
    excited_contract = (
        ers.get("excited_protocol_contract_v1")
        if isinstance(ers, dict) and isinstance(ers.get("excited_protocol_contract_v1"), dict)
        else None
    )

    qpe_three_de = rsum.get("qpe_three_pack_deterministic_energy_est")
    qpe_three_ke = rsum.get("qpe_three_pack_kitaev_energy_est")
    qpe_three_ie = rsum.get("qpe_three_pack_info_theory_energy_est")

    return {
        "schema": "methods_resource_unified_v1",
        "classical_backend_id": rsum.get("classical_backend_id"),
        "classical_benchmark_backend_yaml": rsum.get("classical_benchmark_backend_yaml"),
        "quantum_algorithm_yaml": rsum.get("quantum_algorithm_yaml"),
        "quantum_algorithm_factory_yaml": rsum.get("quantum_algorithm_factory_yaml"),
        "resource_summary": rs_pick,
        "qpe_demo_track": qpe_compact,
        "run_summary_qpe_demo_track_ran": rsum.get("qpe_demo_track_ran"),
        "run_summary_qpe_three_pack_ran": rsum.get("qpe_three_pack_ran"),
        "qpe_three_pack_deterministic_energy_est": qpe_three_de,
        "qpe_three_pack_kitaev_energy_est": qpe_three_ke,
        "qpe_three_pack_info_theory_energy_est": qpe_three_ie,
        "qpe_open_stack_contract_v1": qpe_contract_d,
        "run_summary_vqs_track_ran": rsum.get("vqs_track_ran"),
        "vqs_open_stack_contract_v1": vqs_contract_d,
        "excited_protocol_contract_v1_present": excited_contract is not None,
        "tket_first_compiled_circuit_probe_schema": tket_schema,
        "classical_benchmark_active": classical_active,
        "classical_benchmark_summary_schema": sum_schema,
        "classical_benchmark_recommended_baseline_policy": rec_policy,
        "classical_benchmark_recommended_baseline_method": rec_method,
        "classical_benchmark_recommended_baseline_energy_au": rec_energy,
        "classical_benchmark_best_method": best_m,
        "classical_benchmark_best_energy_au": best_e,
    }

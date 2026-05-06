"""Unified Methods-facing resource slice for export (QPE track + variational + TKET probe)."""

from __future__ import annotations

from typing import Any


def build_methods_resource_unified_v1(pipeline_row: dict[str, Any]) -> dict[str, Any]:
    """
    Merge ``resource_summary``, optional ``qpe_demo_track``, and parity TKET probe into one blob.

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
        qpe_compact = {
            "schema": qpe.get("schema"),
            "has_kitaev_dense": qpe.get("kitaev_ground_energy_dense") is not None,
            "has_bayesian_stub": qpe.get("bayesian_phase_map_toy") is not None,
        }

    tket_schema = tket.get("schema") if isinstance(tket, dict) else None

    return {
        "schema": "methods_resource_unified_v1",
        "resource_summary": rs_pick,
        "qpe_demo_track": qpe_compact,
        "run_summary_qpe_demo_track_ran": rsum.get("qpe_demo_track_ran"),
        "tket_first_compiled_circuit_probe_schema": tket_schema,
    }

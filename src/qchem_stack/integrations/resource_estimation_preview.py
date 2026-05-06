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
    base: dict[str, Any] = {
        "schema": "resource_estimation_preview_v1",
        "mode": "pipeline" if pipeline_row else "config_only",
        "epistemic_bound": (
            "Open-stack preview only: no HQC/Nexus currency, no vendor L0 resource guarantee."
        ),
        "qpe_demo_track_after_variational": cfg.quantum.qpe_demo_track_after_variational,
        "qpe_pipeline_integration": cfg.quantum.qpe_pipeline_integration,
        "parity_integrations_tket_first_circuit_stats": pi.tket_first_circuit_stats,
        "use_pauli_protocol": cfg.quantum.use_pauli_protocol,
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
    return base

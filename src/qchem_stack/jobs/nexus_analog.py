"""
Local stand-in for Nexus / ``qnexus`` project labels + HQC-style **unit** accounting.

There is **no** Quantinuum API, billing contract, or currency conversion—only reproducible
floats from :class:`qchem_stack.jobs.cost.CostEstimate` and YAML ``nexus_analog`` weights.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.config import ExperimentConfig, NexusAnalogSpec
from qchem_stack.jobs.cost import CostEstimate


def nexus_analog_ledger_from_spec(
    rows: list[dict[str, Any]], na: NexusAnalogSpec
) -> dict[str, Any] | None:
    """If ``na.enabled``, return a machine-readable HQC-style ledger; otherwise ``None``."""
    if not na.enabled:
        return None
    if not rows:
        return {
            "schema": "nexus_analog_v1",
            "project_label": na.project_label,
            "hqc_units": 0.0,
            "note": "empty_resource_rows",
        }
    ce = CostEstimate.from_resource_rows(
        rows,
        unit_per_circuit=float(na.unit_per_circuit),
        unit_per_shot=float(na.unit_per_shot),
        unit_per_depth=float(na.unit_per_depth),
    )
    return {
        "schema": "nexus_analog_v1",
        "project_label": na.project_label,
        "hqc_units": float(ce.hqc_units),
        "estimated_circuits": ce.estimated_circuits,
        "estimated_total_shots": ce.estimated_total_shots,
        "native_twoq_depth_sum": ce.native_twoq_depth_sum,
    }


def nexus_analog_ledger_from_rows(
    rows: list[dict[str, Any]],
    cfg: ExperimentConfig,
) -> dict[str, Any] | None:
    """If ``nexus_analog.enabled``, return a machine-readable HQC-style ledger dict."""
    return nexus_analog_ledger_from_spec(rows, cfg.nexus_analog)


def nexus_analog_billing_for_job_result(
    rows: list[dict[str, Any]], na: NexusAnalogSpec | None
) -> dict[str, Any]:
    """Async worker billing: use YAML weights when a :class:`NexusAnalogSpec` is on the protocol."""
    if na is not None and na.enabled:
        led = nexus_analog_ledger_from_spec(rows, na)
        if led is not None:
            return led
    return default_nexus_analog_for_job_result(rows)


def default_nexus_analog_for_job_result(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """When pickled protocol is processed without :class:`ExperimentConfig`, use unit defaults."""
    if not rows:
        return {
            "schema": "nexus_analog_v1",
            "project_label": "default",
            "hqc_units": 0.0,
            "note": "config_defaults",
        }
    ce = CostEstimate.from_resource_rows(rows)
    return {
        "schema": "nexus_analog_v1",
        "project_label": "default",
        "hqc_units": float(ce.hqc_units),
        "estimated_circuits": ce.estimated_circuits,
        "estimated_total_shots": ce.estimated_total_shots,
        "native_twoq_depth_sum": ce.native_twoq_depth_sum,
        "note": "config_defaults",
    }

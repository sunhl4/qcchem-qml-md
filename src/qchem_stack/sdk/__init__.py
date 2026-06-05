"""Stable integrator facade for qchem-stack (re-exports only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.config.scenarios import SCENARIOS, list_scenarios_text
from qchem_stack.orchestration.pipeline import run_pipeline_from_config, run_pipeline_sync
from qchem_stack.protocols.parity_criteria_export import export_parity_criteria_table
from qchem_stack.protocols.workflow_preview import workflow_preview_payload
from qchem_stack.repro.export import repro_dict_for_strict_json, repro_json_dumps


def export_parity_table(
    config_path: str | Path,
    *,
    results_path: str | Path | None = None,
) -> dict[str, Any]:
    """Export Methods-style parity table JSON (same as ``qchem-export-parity`` CLI)."""
    return export_parity_criteria_table(config_path, results_path=results_path)


__all__ = [
    "ExperimentConfig",
    "SCENARIOS",
    "export_parity_table",
    "list_scenarios_text",
    "load_experiment_config",
    "repro_dict_for_strict_json",
    "repro_json_dumps",
    "run_pipeline_from_config",
    "run_pipeline_sync",
    "workflow_preview_payload",
]

"""Stable integrator facade for qchem-stack (re-exports only)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.config.scenarios import SCENARIOS, list_scenarios_text
from qchem_stack.orchestration.pipeline import run_pipeline_from_config, run_pipeline_sync
from qchem_stack.protocols.workflow_preview import workflow_preview_payload
from qchem_stack.repro.export import repro_dict_for_strict_json, repro_json_dumps


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in (here.parents[3], here.parents[2]):
        if (candidate / "scripts" / "export_parity_criteria_table.py").is_file():
            return candidate
    raise RuntimeError("export_parity_criteria_table.py not found from sdk package path")


def export_parity_table(
    config_path: str | Path,
    *,
    results_path: str | Path | None = None,
) -> dict[str, Any]:
    """Export Methods-style parity table JSON (same as ``qchem-export-parity`` CLI)."""
    root = _repo_root()
    cmd = [
        sys.executable,
        str(root / "scripts" / "export_parity_criteria_table.py"),
        str(Path(config_path).resolve()),
    ]
    if results_path is not None:
        cmd.extend(["--results", str(Path(results_path).resolve())])
    env = {
        **os.environ,
        "PYTHONPATH": str(root / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""),
    }
    proc = subprocess.run(
        cmd,
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "export_parity_criteria_table failed")
    out = json.loads(proc.stdout)
    if not isinstance(out, dict):
        raise ValueError("parity export must return a JSON object")
    return out


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

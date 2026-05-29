"""Summary and per-round JSON serialization for the MD validation loop."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.md_bridge.md_loop_config import MdValidationLoopConfig, MdValidationRoundLog


def round_log_to_jsonable(log: MdValidationRoundLog) -> dict[str, Any]:
    d = asdict(log)
    d["frames"] = [asdict(fr) for fr in log.frames]
    return d


def json_default(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return float(obj)
    if hasattr(obj, "item"):
        return obj.item()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def write_round_metrics(
    out: Path, round_i: int, log: MdValidationRoundLog, debug_by_idx: dict[int, dict[str, Any]]
) -> None:
    payload = {
        "round": round_log_to_jsonable(log),
        "frames_debug": {str(k): v for k, v in debug_by_idx.items()},
    }
    (out / f"validation_round_{round_i}.json").write_text(
        json.dumps(payload, indent=2, default=json_default),
        encoding="utf-8",
    )


def build_md_validation_summary(
    *,
    experiment_yaml: Path,
    output_dir: Path,
    config: MdValidationLoopConfig,
    n_total_frames: int,
    round_logs: list[MdValidationRoundLog],
    converged: bool,
    species_list: list[str],
    accuracy_threshold_hartree: float | None = None,
) -> dict[str, Any]:
    threshold = (
        float(accuracy_threshold_hartree)
        if accuracy_threshold_hartree is not None
        else float(config.energy_tolerance_hartree)
    )
    round_max = [
        float(r.max_abs_delta_hartree)
        for r in round_logs
        if r.max_abs_delta_hartree == r.max_abs_delta_hartree
    ]
    global_max_abs = max(round_max) if round_max else float("nan")
    science_kpi_met = bool(global_max_abs == global_max_abs and global_max_abs < threshold)
    last_shift = None
    if round_logs:
        tm = round_logs[-1].training_metrics or {}
        last_shift = tm.get("validation_energy_shift_hartree")
    return {
        "experiment_yaml": str(experiment_yaml.resolve()),
        "output_dir": str(output_dir.resolve()),
        "config": asdict(config),
        "accuracy_threshold_hartree": threshold,
        "max_abs_delta_hartree": global_max_abs,
        "validation_energy_shift_hartree": last_shift,
        "science_kpi_met": science_kpi_met,
        "n_total_frames": n_total_frames,
        "rounds": [round_log_to_jsonable(log) for log in round_logs],
        "converged": bool(converged),
        "species_list": list(species_list),
        "force_field_backend": config.force_field_backend,
        "qmlff_preset": config.qmlff_preset,
    }


def write_md_validation_summary(output_dir: Path, summary: dict[str, Any]) -> None:
    (output_dir / "md_validation_summary.json").write_text(
        json.dumps(summary, indent=2, default=json_default),
        encoding="utf-8",
    )

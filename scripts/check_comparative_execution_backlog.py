#!/usr/bin/env python3
"""Validate strict execution backlog YAML (program milestones + evidence)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

ALLOWED_PHASE_STATUS = {"todo", "in_progress", "done", "blocked"}
ALLOWED_TASK_STATUS = {"todo", "in_progress", "done", "blocked"}
REQUIRED_TOP_KEYS = {"version", "program", "source_of_truth", "phases"}
REQUIRED_PHASE_KEYS = {"id", "title", "day_range", "status", "objectives", "tasks"}
REQUIRED_TASK_KEYS = {
    "id",
    "title",
    "owner",
    "status",
    "target_files",
    "tests",
    "acceptance_criteria",
    "evidence",
}


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("backlog yaml top level must be a mapping")
    return data


def _require_keys(obj: dict[str, Any], required: set[str], where: str) -> list[str]:
    missing = sorted(required - set(obj.keys()))
    return [f"{where}: missing keys {missing}"] if missing else []


def _validate_task(task: dict[str, Any], where: str) -> list[str]:
    errors: list[str] = []
    errors.extend(_require_keys(task, REQUIRED_TASK_KEYS, where))
    if errors:
        return errors

    status = task["status"]
    if status not in ALLOWED_TASK_STATUS:
        errors.append(f"{where}: invalid task status {status!r}")
    for key in ("target_files", "tests", "acceptance_criteria", "evidence"):
        if not isinstance(task[key], list):
            errors.append(f"{where}: {key} must be a list")
    if not isinstance(task["id"], str) or not task["id"]:
        errors.append(f"{where}: id must be non-empty string")
    if not isinstance(task["title"], str) or not task["title"]:
        errors.append(f"{where}: title must be non-empty string")
    if not isinstance(task["owner"], str) or not task["owner"]:
        errors.append(f"{where}: owner must be non-empty string")
    if status == "done" and not task["evidence"]:
        errors.append(f"{where}: done task must include at least one evidence entry")
    return errors


def _validate_phase(phase: dict[str, Any], idx: int) -> list[str]:
    where = f"phase[{idx}]"
    errors: list[str] = []
    errors.extend(_require_keys(phase, REQUIRED_PHASE_KEYS, where))
    if errors:
        return errors

    status = phase["status"]
    if status not in ALLOWED_PHASE_STATUS:
        errors.append(f"{where}: invalid phase status {status!r}")
    if not isinstance(phase["id"], str) or not phase["id"]:
        errors.append(f"{where}: id must be non-empty string")
    if not isinstance(phase["title"], str) or not phase["title"]:
        errors.append(f"{where}: title must be non-empty string")
    if not isinstance(phase["day_range"], str) or not phase["day_range"]:
        errors.append(f"{where}: day_range must be non-empty string")
    if not isinstance(phase["objectives"], list) or not phase["objectives"]:
        errors.append(f"{where}: objectives must be a non-empty list")
    if not isinstance(phase["tasks"], list) or not phase["tasks"]:
        errors.append(f"{where}: tasks must be a non-empty list")
        return errors

    task_ids: set[str] = set()
    for task_idx, task in enumerate(phase["tasks"]):
        if not isinstance(task, dict):
            errors.append(f"{where}.tasks[{task_idx}]: task must be mapping")
            continue
        task_where = f"{where}.tasks[{task_idx}]"
        errors.extend(_validate_task(task, task_where))
        task_id = task.get("id")
        if isinstance(task_id, str):
            if task_id in task_ids:
                errors.append(f"{where}: duplicated task id {task_id!r}")
            task_ids.add(task_id)
    return errors


def validate_backlog(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(_require_keys(data, REQUIRED_TOP_KEYS, "top"))
    if errors:
        return errors

    if not isinstance(data["version"], int):
        errors.append("top.version must be integer")
    if not isinstance(data["program"], str) or not data["program"]:
        errors.append("top.program must be non-empty string")

    source = data["source_of_truth"]
    if not isinstance(source, dict):
        errors.append("top.source_of_truth must be mapping")
    else:
        for key in ("plan_doc", "contract", "capability_surface"):
            v = source.get(key)
            if not isinstance(v, str) or not v:
                errors.append(f"top.source_of_truth.{key} must be non-empty string")

    phases = data["phases"]
    if not isinstance(phases, list) or not phases:
        errors.append("top.phases must be non-empty list")
        return errors

    phase_ids: set[str] = set()
    for idx, phase in enumerate(phases):
        if not isinstance(phase, dict):
            errors.append(f"phase[{idx}] must be mapping")
            continue
        errors.extend(_validate_phase(phase, idx))
        phase_id = phase.get("id")
        if isinstance(phase_id, str):
            if phase_id in phase_ids:
                errors.append(f"duplicated phase id {phase_id!r}")
            phase_ids.add(phase_id)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("docs/execution/comparative_execution_backlog.yaml"),
        help="Backlog yaml path",
    )
    args = parser.parse_args()

    try:
        data = _load_yaml(args.path)
        errors = validate_backlog(data)
    except FileNotFoundError:
        sys.stderr.write(f"backlog file not found: {args.path}\n")
        return 1
    except yaml.YAMLError as exc:
        sys.stderr.write(f"invalid yaml: {exc}\n")
        return 1
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1

    if errors:
        sys.stderr.write("backlog validation failed:\n")
        for err in errors:
            sys.stderr.write(f"- {err}\n")
        return 1
    print(f"backlog validation passed: {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

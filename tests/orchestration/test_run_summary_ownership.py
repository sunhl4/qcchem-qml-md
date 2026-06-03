"""Ensure run_summary and parity_snapshot have a single canonical writer path."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORCH = ROOT / "src" / "qchem_stack" / "orchestration"


def _find_assignments_to_key(module_path: Path, repro_key: str) -> list[str]:
    """Return function names that assign repro[repro_key] = ..."""
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for child in ast.walk(node):
            if not isinstance(child, ast.Assign):
                continue
            for target in child.targets:
                if not isinstance(target, ast.Subscript):
                    continue
                if not isinstance(target.value, ast.Name) or target.value.id != "repro":
                    continue
                sl = target.slice
                if isinstance(sl, ast.Constant) and sl.value == repro_key:
                    hits.append(node.name)
                    break
    return hits


def test_run_summary_only_attach_run_summary_assigns() -> None:
    writers: list[str] = []
    for path in ORCH.glob("*.py"):
        if path.name == "repro_summary.py":
            continue
        for fn in _find_assignments_to_key(path, "run_summary"):
            writers.append(f"{path.name}:{fn}")
    assert writers == [], f"unexpected run_summary writers: {writers}"


def test_attach_run_summary_is_canonical_writer() -> None:
    writers = _find_assignments_to_key(ORCH / "repro_summary.py", "run_summary")
    assert "attach_run_summary" in writers


def test_parity_finalize_does_not_write_run_summary() -> None:
    writers = _find_assignments_to_key(ORCH / "parity_finalize.py", "run_summary")
    assert writers == []

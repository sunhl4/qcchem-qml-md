from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_backlog_validator_passes_on_repository_backlog() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "check_inquanto_tangelo_comparative_backlog.py"
    backlog = root / "docs" / "execution" / "inquanto_tangelo_comparative_backlog.yaml"
    cp = subprocess.run(
        [sys.executable, str(script), "--path", str(backlog)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode == 0, cp.stderr
    assert "backlog validation passed" in cp.stdout


def test_backlog_validator_rejects_done_without_evidence(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "check_inquanto_tangelo_comparative_backlog.py"
    backlog = tmp_path / "bad.yaml"
    backlog.write_text(
        """
version: 1
program: demo
source_of_truth:
  plan_doc: docs/execution/plan.md
  contract: src/qchem_stack/protocols/inquanto_contract.py
  capability_surface: src/qchem_stack/api/app.py
phases:
  - id: A
    title: phase
    day_range: Day1-Day2
    status: in_progress
    objectives: [obj]
    tasks:
      - id: A-001
        title: task
        owner: x
        status: done
        target_files: [a.py]
        tests: [tests/test_a.py]
        acceptance_criteria: [crit]
        evidence: []
""".strip(),
        encoding="utf-8",
    )
    cp = subprocess.run(
        [sys.executable, str(script), "--path", str(backlog)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode != 0
    assert "done task must include at least one evidence entry" in cp.stderr

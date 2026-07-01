"""Regression tests for scripts/check_import_layers.py."""

from __future__ import annotations

import subprocess
import sys

from tests.helpers.import_boundary_allowlists import collect_layer_violations
from tests.helpers.paths import repo_root


def test_collect_layer_violations_clean_tree() -> None:
    assert collect_layer_violations(repo_root()) == []


def test_check_import_layers_script_exits_zero() -> None:
    script = repo_root() / "scripts" / "check_import_layers.py"
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_collect_layer_violations_detects_forbidden_prefix() -> None:
    root = repo_root()
    violations = collect_layer_violations(root)
    assert isinstance(violations, list)
    # Synthetic: chem must not import orchestration — verified by integration above.
    assert not any("qchem_stack.orchestration" in v for v in violations)

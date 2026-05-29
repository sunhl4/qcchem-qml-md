"""smoke_pipeline --precomputed-only (no PySCF required)."""

from __future__ import annotations

import os
import subprocess
import sys

from tests.helpers.paths import repo_root


def test_smoke_pipeline_precomputed_only_subprocess() -> None:
    root = repo_root()
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{root / 'src'}{os.pathsep}{root}"
    proc = subprocess.run(
        [sys.executable, str(root / "scripts" / "smoke_pipeline.py"), "--precomputed-only"],
        cwd=str(root),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "precomputed_bundle" in proc.stdout

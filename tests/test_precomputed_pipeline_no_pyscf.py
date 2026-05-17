"""Precomputed bundle lane in a fresh interpreter with PySCF import blocked."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.no_pyscf
def test_precomputed_lane_without_pyscf_import() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_precomputed_bundle.yaml"
    script = f"""
import importlib.abc
import sys
from pathlib import Path

class _PyscfBlocker(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "pyscf" or fullname.startswith("pyscf."):
            msg = "pyscf blocked for no_pyscf test"
            raise ImportError(msg)
        return None

sys.meta_path.insert(0, _PyscfBlocker())

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync

root = Path({str(root)!r})
p = root / "configs" / "example_h2_precomputed_bundle.yaml"
cfg = load_experiment_config(p)
out = run_pipeline_sync(cfg, cfg_path=p)
assert out["pre_quantum_input"]["source"] == "precomputed_bundle"
print("ok")
"""
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=root,
        capture_output=True,
        text=True,
        env={**dict(**__import__("os").environ), "PYTHONPATH": f"{root / 'src'}:{root}"},
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"subprocess failed ({proc.returncode}):\nstdout={proc.stdout}\nstderr={proc.stderr}"
        )

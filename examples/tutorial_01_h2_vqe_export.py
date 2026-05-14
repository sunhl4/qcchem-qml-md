#!/usr/bin/env python3
"""Tutorial 1: H2 packaged VQE + Pauli protocol, then parity export (config + optional run JSON)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        print("tutorial_01: skip (install PySCF / pip install qchem-stack[chem])")
        return 0
    root = Path(__file__).resolve().parents[1]
    cfg = root / "configs" / "example_h2.yaml"
    env = {**__import__("os").environ, "PYTHONPATH": str(root / "src")}
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    out = run_pipeline_sync(load_experiment_config(cfg), cfg_path=cfg)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        tmp = Path(f.name)
    try:
        subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "export_parity_criteria_table.py"),
                str(cfg),
                "--results",
                str(tmp),
            ],
            cwd=str(root),
            check=True,
            env=env,
        )
    finally:
        tmp.unlink(missing_ok=True)
    print("tutorial_01: pipeline + export OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

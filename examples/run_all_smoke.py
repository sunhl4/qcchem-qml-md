#!/usr/bin/env python3
"""Run packaged tutorial scripts (best-effort; skips when PySCF missing)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    scripts = [
        root / "examples" / "tutorial_01_h2_vqe_export.py",
        root / "examples" / "tutorial_02_uccsd_pipeline.py",
        root / "examples" / "tutorial_03_qpe_zne_paths.py",
        root / "examples" / "tutorial_04_uccsd_below_scf.py",
        root / "examples" / "toy_dmrg_spin_chain.py",
    ]
    for s in scripts:
        if s.name == "toy_dmrg_spin_chain.py":
            argv = [sys.executable, str(s), "--L", "8", "--m-warmup", "10", "--m-sweeps", "10,10", "--exact"]
        else:
            argv = [sys.executable, str(s)]
        proc = subprocess.run(argv, cwd=str(root), check=False)
        if proc.returncode != 0:
            return int(proc.returncode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

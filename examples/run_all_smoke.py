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
    ]
    for s in scripts:
        proc = subprocess.run([sys.executable, str(s)], cwd=str(root), check=False)
        if proc.returncode != 0:
            return int(proc.returncode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

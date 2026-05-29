#!/usr/bin/env python3
"""Optional nbconvert smoke: execute notebooks marked with colab metadata."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("*.ipynb"))


def main() -> int:
    if not NOTEBOOKS:
        print("No notebooks found; skipping.")
        return 0
    try:
        import nbconvert  # noqa: F401
    except ImportError:
        print("nbconvert not installed; skipping notebook CI smoke.")
        return 0
    failed = 0
    for nb in NOTEBOOKS:
        cmd = [
            sys.executable,
            "-m",
            "jupyter",
            "nbconvert",
            "--to",
            "notebook",
            "--execute",
            str(nb),
            "--output",
            str(nb.with_suffix(".executed.ipynb")),
        ]
        print("Running", nb.name)
        rc = subprocess.call(cmd, cwd=str(ROOT))
        if rc != 0:
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

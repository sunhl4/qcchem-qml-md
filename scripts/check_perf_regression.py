#!/usr/bin/env python3
"""Soft perf regression check (nightly): compare pytest -m perf wall time to baseline JSON."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs" / "engineering" / "perf_baseline.json"
WARN_RATIO = 1.20


def main() -> int:
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q", "-m", "perf", "--tb=no"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stderr)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode
    if BASELINE.is_file():
        data = json.loads(BASELINE.read_text(encoding="utf-8"))
        prev = float(data.get("perf_wall_seconds", 0))
        if prev > 0 and elapsed > prev * WARN_RATIO:
            print(
                f"perf regression warn: {elapsed:.1f}s > {WARN_RATIO:.0%} of baseline {prev:.1f}s",
                file=sys.stderr,
            )
    else:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(
            json.dumps({"perf_wall_seconds": elapsed, "schema": "perf_baseline_v1"}, indent=2),
            encoding="utf-8",
        )
        print(f"wrote baseline {BASELINE} ({elapsed:.1f}s)")
    print(f"perf_wall_seconds={elapsed:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

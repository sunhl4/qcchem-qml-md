#!/usr/bin/env python3
"""Soft perf regression check (nightly): compare pytest -m perf wall time to baseline JSON."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs" / "engineering" / "perf_baseline.json"
WARN_RATIO = 1.20


def _write_baseline(elapsed: float) -> None:
    BASELINE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE.write_text(
        json.dumps(
            {
                "perf_wall_seconds": round(elapsed, 3),
                "schema": "perf_baseline_v1",
                "note": "Updated by scripts/check_perf_regression.py",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"wrote baseline {BASELINE} ({elapsed:.1f}s)")


def _write_report(path: Path, *, elapsed: float, prev: float, strict: bool, passed: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema": "perf_regression_report_v1",
                "perf_wall_seconds": round(elapsed, 3),
                "baseline_seconds": round(prev, 3) if prev > 0 else None,
                "warn_ratio": WARN_RATIO,
                "strict": strict,
                "passed": passed,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional JSON report path for CI artifact upload",
    )
    args = parser.parse_args(argv)
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

    strict = os.getenv("QCHEM_PERF_REGRESSION_STRICT", "").lower() in {"1", "true", "yes"}
    prev = 0.0
    if BASELINE.is_file():
        data = json.loads(BASELINE.read_text(encoding="utf-8"))
        prev = float(data.get("perf_wall_seconds", 0))

    passed = True
    if prev <= 0:
        _write_baseline(elapsed)
    elif elapsed > prev * WARN_RATIO:
        msg = f"perf regression: {elapsed:.1f}s > {WARN_RATIO:.0%} of baseline {prev:.1f}s"
        print(msg, file=sys.stderr)
        passed = False
        if strict:
            if args.report is not None:
                _write_report(args.report, elapsed=elapsed, prev=prev, strict=strict, passed=False)
            return 1

    print(f"perf_wall_seconds={elapsed:.2f}")
    if args.report is not None:
        _write_report(args.report, elapsed=elapsed, prev=prev, strict=strict, passed=passed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

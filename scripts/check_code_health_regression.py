#!/usr/bin/env python3
"""Fail when code-health large-file metrics regress above baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE_JSON = ROOT / "docs" / "engineering" / "code_health_baseline.snapshot.json"


def main() -> int:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "code_health_baseline",
        ROOT / "scripts" / "code_health_baseline.py",
    )
    if spec is None or spec.loader is None:
        print("failed to load code_health_baseline.py", file=sys.stderr)
        return 1
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    report = mod.build_report()
    if not BASELINE_JSON.is_file():
        BASELINE_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"wrote baseline snapshot {BASELINE_JSON}")
        return 0

    prev = json.loads(BASELINE_JSON.read_text(encoding="utf-8"))
    over_500 = int(report.get("files_over_500_lines", 0))
    prev_over_500 = int(prev.get("files_over_500_lines", 0))
    if over_500 > prev_over_500:
        print(
            f"code health regression: files_over_500_lines {over_500} > baseline {prev_over_500}",
            file=sys.stderr,
        )
        return 1

    prev_any = {
        row["path"]: int(row["count"])
        for row in prev.get("dict_str_any_top", [])
        if isinstance(row, dict) and "path" in row and "count" in row
    }
    for row in report.get("dict_str_any_top", []):
        if not isinstance(row, dict):
            continue
        path = str(row.get("path", ""))
        if not path.startswith("src/qchem_stack/protocols/"):
            continue
        count = int(row.get("count", 0))
        baseline = prev_any.get(path)
        if baseline is not None and count > baseline:
            print(
                f"code health regression: dict[str, Any] in {path} {count} > baseline {baseline}",
                file=sys.stderr,
            )
            return 1

    print(f"code_health_ok files_over_500_lines={over_500}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

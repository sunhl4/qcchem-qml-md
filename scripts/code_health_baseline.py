#!/usr/bin/env python3
"""Read-only code-health metrics for style optimization (P0 baseline)."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src" / "qchem_stack"
CONFIG_ROOT = SRC_ROOT / "config"
LINE_THRESHOLD = 400
DICT_ANY_PATTERN = re.compile(r"dict\s*\[\s*str\s*,\s*Any\s*\]")


def _py_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.py"))


def _line_counts(files: list[Path]) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for path in files:
        try:
            n = len(path.read_text(encoding="utf-8").splitlines())
        except OSError:
            continue
        if n > LINE_THRESHOLD:
            rel = path.relative_to(REPO_ROOT).as_posix()
            rows.append((n, rel))
    rows.sort(reverse=True)
    return rows


def _dict_any_counts(files: list[Path], top_n: int = 25) -> list[tuple[int, str]]:
    counter: Counter[str] = Counter()
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        hits = len(DICT_ANY_PATTERN.findall(text))
        if hits:
            counter[path.relative_to(REPO_ROOT).as_posix()] = hits
    return counter.most_common(top_n)


def build_report() -> dict[str, object]:
    src_files = _py_files(SRC_ROOT)
    large_files = [{"lines": n, "path": p} for n, p in _line_counts(src_files)]
    dict_any_top = [{"count": c, "path": p} for p, c in _dict_any_counts(src_files)]
    over_500 = sum(1 for n, _ in _line_counts(src_files) if n > 500)
    return {
        "src_root": SRC_ROOT.relative_to(REPO_ROOT).as_posix(),
        "line_threshold": LINE_THRESHOLD,
        "python_file_count": len(src_files),
        "files_over_line_threshold": len(large_files),
        "files_over_500_lines": over_500,
        "large_files": large_files,
        "dict_str_any_top": dict_any_top,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        type=Path,
        default=None,
        help="Write JSON report to this path (relative to repo root or absolute).",
    )
    args = parser.parse_args()
    report = build_report()
    text = json.dumps(report, indent=2, ensure_ascii=False)
    print(text)
    if args.write is not None:
        out = args.write if args.write.is_absolute() else REPO_ROOT / args.write
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {out.relative_to(REPO_ROOT)}", flush=True)


if __name__ == "__main__":
    main()

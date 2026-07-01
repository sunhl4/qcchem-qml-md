#!/usr/bin/env python3
"""Per-package coverage thresholds (post-pytest htmlcov)."""

from __future__ import annotations

import argparse
import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Package prefix under src/qchem_stack -> minimum line coverage percent.
# v1.1 release floors reflect current measured baselines; raise incrementally per release.
THRESHOLDS: dict[str, int] = {
    "src/qchem_stack/config": 65,
    "src/qchem_stack/repro": 22,
    "src/qchem_stack/protocols": 80,
    "src/qchem_stack/orchestration": 75,
    "src/qchem_stack/quantum": 70,
    "src/qchem_stack/backends": 70,
    "src/qchem_stack/chem": 75,
    "src/qchem_stack/chem/kernels": 70,
    "src/qchem_stack/jobs": 62,
    "src/qchem_stack/md_bridge": 68,
    "src/qchem_stack/mitigation": 70,
    "src/qchem_stack/api": 70,
    "src/qchem_stack/integrations": 60,
    "src/qchem_stack/contracts": 75,
    "src/qchem_stack/sdk": 75,
}

_ROW = re.compile(
    r'<tr class="region">.*?<td class="name"><a[^>]*>(?P<path>.*?)</a></td>.*?'
    r'<td data-ratio="(?P<covered>\d+) (?P<stmts>\d+)">',
    re.DOTALL,
)


def _clean_path(raw: str) -> str:
    text = unescape(re.sub(r"<[^>]+>", "", raw))
    return text.replace("\\", "/")


def _parse_index(html: str) -> dict[str, tuple[int, int]]:
    """Return rel_path -> (statements, covered)."""
    out: dict[str, tuple[int, int]] = {}
    for m in _ROW.finditer(html):
        rel = _clean_path(m.group("path"))
        covered = int(m.group("covered"))
        stmts = int(m.group("stmts"))
        out[rel] = (stmts, covered)
    return out


def _aggregate(prefix: str, rows: dict[str, tuple[int, int]]) -> tuple[int, int]:
    total = covered = 0
    norm = prefix.replace("\\", "/").rstrip("/") + "/"
    for rel, (stmts, cov) in rows.items():
        rel_norm = rel.replace("\\", "/")
        if rel_norm.startswith(norm) or rel_norm == prefix.replace("\\", "/").rstrip("/"):
            total += stmts
            covered += cov
    return total, covered


def _resolve_prefix(package: str) -> str:
    key = package.replace("\\", "/").strip("/")
    if key.startswith("src/qchem_stack/"):
        return key
    if key.startswith("qchem_stack/"):
        return "src/" + key
    return f"src/qchem_stack/{key}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check per-package coverage floors.")
    parser.add_argument(
        "--package",
        help="Check only this package prefix (e.g. md_bridge or src/qchem_stack/md_bridge).",
    )
    parser.add_argument(
        "--min",
        type=int,
        help="Override minimum percent for --package (ignored without --package).",
    )
    args = parser.parse_args()

    index_path = ROOT / "htmlcov" / "index.html"
    if not index_path.is_file():
        print("htmlcov/index.html missing; run pytest with --cov first", file=sys.stderr)
        return 1
    rows = _parse_index(index_path.read_text(encoding="utf-8"))
    if not rows:
        print("htmlcov/index.html parsed zero file rows; update parser?", file=sys.stderr)
        return 1

    if args.package:
        prefix = _resolve_prefix(args.package)
        min_pct = args.min if args.min is not None else THRESHOLDS.get(prefix, 0)
        thresholds = {prefix: min_pct}
    else:
        thresholds = THRESHOLDS

    failures: list[str] = []
    for prefix, min_pct in thresholds.items():
        total, covered = _aggregate(prefix, rows)
        if total == 0:
            failures.append(f"{prefix}: no statements found in coverage report")
            continue
        pct = 100.0 * covered / total
        if pct + 1e-9 < min_pct:
            failures.append(f"{prefix}: {pct:.1f}% < {min_pct}% ({covered}/{total} lines)")
    if failures:
        print("Coverage threshold failures:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("Per-package coverage thresholds OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Per-package coverage thresholds (post-pytest htmlcov)."""

from __future__ import annotations

import re
import sys
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Package prefix under src/qchem_stack -> minimum line coverage percent.
THRESHOLDS: dict[str, int] = {
    "src/qchem_stack/config": 85,
    "src/qchem_stack/repro": 85,
    "src/qchem_stack/protocols": 80,
    "src/qchem_stack/orchestration": 75,
    "src/qchem_stack/chem/kernels": 70,
    "src/qchem_stack/jobs": 70,
    "src/qchem_stack/md_bridge": 65,
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


def main() -> int:
    index_path = ROOT / "htmlcov" / "index.html"
    if not index_path.is_file():
        print("htmlcov/index.html missing; run pytest with --cov first", file=sys.stderr)
        return 1
    rows = _parse_index(index_path.read_text(encoding="utf-8"))
    if not rows:
        print("htmlcov/index.html parsed zero file rows; update parser?", file=sys.stderr)
        return 1
    failures: list[str] = []
    for prefix, min_pct in THRESHOLDS.items():
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

#!/usr/bin/env python3
"""Generate docs/execution/INDEX.md from comparative execution backlog phases."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "docs" / "execution" / "comparative_execution_backlog.yaml"
INDEX = ROOT / "docs" / "execution" / "INDEX.md"


def main() -> int:
    if not BACKLOG.is_file():
        print(f"Missing {BACKLOG}", file=sys.stderr)
        return 1
    data = yaml.safe_load(BACKLOG.read_text(encoding="utf-8"))
    phases = data.get("phases") or []
    lines = [
        "# Execution evidence index",
        "",
        "<!-- generated: scripts/execution_doc_index.py -->",
        "",
        "Canonical backlog: `comparative_execution_backlog.yaml`. Historical copies under `archive/` are read-only.",
        "",
        "| Phase | Title | Status |",
        "|-------|-------|--------|",
    ]
    for ph in phases:
        if not isinstance(ph, dict):
            continue
        lines.append(f"| `{ph.get('id', '')}` | {ph.get('title', '')} | {ph.get('status', '')} |")
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {INDEX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

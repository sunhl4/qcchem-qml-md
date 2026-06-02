#!/usr/bin/env python3
"""Verify Docusaurus docs reference existing configs/*.yaml paths."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / "docusaurus-site" / "docs"

_YAML_REF = re.compile(r"configs/[\w./_-]+\.ya?ml")


def main() -> int:
    missing: list[str] = []
    for md in DOC_ROOT.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for rel in _YAML_REF.findall(text):
            path = ROOT / rel
            if not path.is_file():
                missing.append(f"{md.relative_to(ROOT)}: {rel}")
    if missing:
        print("Missing config references:", file=sys.stderr)
        for m in sorted(set(missing)):
            print(f"  {m}", file=sys.stderr)
        return 1
    print("Doc config link check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

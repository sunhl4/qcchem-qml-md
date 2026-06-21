#!/usr/bin/env python3
"""Fail when flat tests/test_*.py files exist at repo tests/ root."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TESTS_ROOT = ROOT / "tests"

ALLOWED_SUBDIRS = frozenset(
    {
        "api",
        "backends",
        "chem",
        "config",
        "contracts",
        "fixtures",
        "helpers",
        "integrations",
        "jobs",
        "md_bridge",
        "mitigation",
        "orchestration",
        "protocols",
        "quantum",
        "repro",
    }
)


def main() -> int:
    flat = sorted(TESTS_ROOT.glob("test_*.py"))
    if flat:
        print(
            "Flat tests at tests/ root are forbidden (use layer subdirectories):", file=sys.stderr
        )
        for path in flat:
            print(f"  {path.relative_to(ROOT)}", file=sys.stderr)
        print("See docs/engineering/test_ownership.md", file=sys.stderr)
        return 1

    unknown_dirs = sorted(
        p.name
        for p in TESTS_ROOT.iterdir()
        if p.is_dir() and p.name not in ALLOWED_SUBDIRS and not p.name.startswith("__")
    )
    if unknown_dirs:
        print(
            "Unknown tests/ subdirectories (add to ALLOWED_SUBDIRS or move tests):",
            file=sys.stderr,
        )
        for name in unknown_dirs:
            print(f"  tests/{name}/", file=sys.stderr)
        return 1

    print("test_layout_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

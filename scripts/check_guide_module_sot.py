#!/usr/bin/env python3
"""Enforce guide↔module single source of truth for selected topics (e.g. GQE)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE_GQE = ROOT / "docusaurus-site" / "docs" / "guide" / "gqe-generative-eigensolver.md"
MAX_GUIDE_LINES = 45
# Guide pages must not contain display-math blocks (those belong in modules deep-reads).
DISPLAY_MATH = re.compile(r"\$\$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="exit 1 on violations (default)")
    parser.parse_args()
    errors: list[str] = []

    if not GUIDE_GQE.is_file():
        errors.append(f"missing {GUIDE_GQE}")
    else:
        text = GUIDE_GQE.read_text(encoding="utf-8")
        n = len(text.splitlines())
        if n > MAX_GUIDE_LINES:
            errors.append(f"GQE guide has {n} lines (max {MAX_GUIDE_LINES}): {GUIDE_GQE}")
        if DISPLAY_MATH.search(text):
            errors.append(
                f"GQE guide must not contain $$ math blocks (SoT is modules deep-read): {GUIDE_GQE}"
            )
        if "modules/quantum/algorithms/gqe" not in text:
            errors.append("GQE guide must link to modules/quantum/algorithms/gqe")

    if errors:
        for e in errors:
            print(e, flush=True)
        return 1
    print("guide/module SoT check OK", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

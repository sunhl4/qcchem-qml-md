#!/usr/bin/env python3
"""Verify Docusaurus python-sdk.md mentions all qchem_stack.sdk public exports."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDK_DOC = ROOT / "docusaurus-site" / "docs" / "reference" / "python-sdk.md"


def main() -> int:
    from qchem_stack.sdk import __all__ as sdk_exports

    text = SDK_DOC.read_text(encoding="utf-8")
    missing = [name for name in sdk_exports if name not in text]
    if missing:
        print(f"python-sdk.md missing exports: {missing}", file=sys.stderr)
        return 1
    # Require at least one fenced import block listing sdk
    if "from qchem_stack.sdk import" not in text:
        print("python-sdk.md must include a qchem_stack.sdk import example", file=sys.stderr)
        return 1
    print(f"sdk doc sync OK ({len(sdk_exports)} exports)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

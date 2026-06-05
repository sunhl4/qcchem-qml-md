#!/usr/bin/env python3
"""Write FastAPI OpenAPI schema to docs/generated/openapi_snapshot.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "generated" / "openapi_snapshot.json"


def _build_schema() -> dict:
    from qchem_stack.api.app import app

    return app.openapi()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if on-disk snapshot differs from current app schema.",
    )
    args = parser.parse_args(argv)
    schema = _build_schema()
    body = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if args.check:
        if not OUT.is_file():
            print(f"missing {OUT}; run without --check", file=sys.stderr)
            return 1
        existing = OUT.read_text(encoding="utf-8")
        if existing != body:
            print(f"openapi snapshot drift: {OUT}", file=sys.stderr)
            return 1
        print("openapi snapshot OK")
        return 0
    OUT.write_text(body, encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

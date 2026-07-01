#!/usr/bin/env python3
"""AST check: chem and quantum must not violate layer import boundaries."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_collect_layer_violations():
    import importlib.util

    path = ROOT / "tests" / "helpers" / "import_boundary_allowlists.py"
    spec = importlib.util.spec_from_file_location("import_boundary_allowlists", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.collect_layer_violations


def main() -> int:
    violations = _load_collect_layer_violations()(ROOT)
    if violations:
        print("Import layer violations:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1
    print("Import layer check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

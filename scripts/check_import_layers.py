#!/usr/bin/env python3
"""AST check: chem and quantum must not import orchestration at module scope."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "qchem_stack"

FORBIDDEN_IMPORTS = {
    "chem": {"orchestration"},
    "quantum": {"orchestration", "pyscf"},
}


def _module_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found


def main() -> int:
    violations: list[str] = []
    for pkg, forbidden in FORBIDDEN_IMPORTS.items():
        base = SRC / pkg
        if not base.is_dir():
            continue
        for py in base.rglob("*.py"):
            if py.name == "__init__.py" and py.parent == base:
                continue
            imports = _module_imports(py)
            bad = imports & forbidden
            if bad:
                rel = py.relative_to(ROOT)
                violations.append(f"{rel}: forbidden top-level imports {sorted(bad)}")
    if violations:
        print("Import layer violations:", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        return 1
    print("Import layer check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

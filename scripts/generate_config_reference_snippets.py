#!/usr/bin/env python3
"""Generate markdown field tables from Pydantic config models."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "docs" / "generated"

SECTIONS = (
    ("mitigation", "qchem_stack.config.mitigation", "MitigationSpec"),
    ("backend", "qchem_stack.config.backend", "BackendSpecConfig"),
    ("quantum", "qchem_stack.config.quantum", "QuantumSpec"),
)

HEADER = "<!-- generated: do not edit; run scripts/generate_config_reference_snippets.py -->\n\n"


def _import_model(module_path: str, class_name: str) -> type:
    import importlib

    mod = importlib.import_module(module_path)
    return getattr(mod, class_name)


def _fields_table(model: type) -> str:
    lines = [
        f"## `{model.__name__}` fields\n",
        "| Field | Type | Required |",
        "|-------|------|----------|",
    ]
    for name, field in model.model_fields.items():
        ann = getattr(field.annotation, "__name__", str(field.annotation))
        req = "yes" if field.is_required() else "no"
        lines.append(f"| `{name}` | `{ann}` | {req} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Exit 1 if generated files would change")
    args = ap.parse_args()
    GENERATED.mkdir(parents=True, exist_ok=True)
    changed = False
    for slug, module_path, class_name in SECTIONS:
        model = _import_model(module_path, class_name)
        content = HEADER + _fields_table(model)
        path = GENERATED / f"config_reference_{slug}_generated.md"
        if path.exists() and path.read_text(encoding="utf-8") == content:
            continue
        if args.check:
            print(f"Would update {path.relative_to(ROOT)}", file=sys.stderr)
            changed = True
        else:
            path.write_text(content, encoding="utf-8")
            print(f"Wrote {path.relative_to(ROOT)}")
    if args.check and changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

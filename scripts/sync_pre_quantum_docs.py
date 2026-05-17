#!/usr/bin/env python3
"""Sync generated pre-quantum docs blocks from code enums."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _replace_block(text: str, start_marker: str, end_marker: str, body: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start < 0 or end < 0 or end < start:
        raise ValueError(f"missing or misordered markers: {start_marker} / {end_marker}")
    head = text[: start + len(start_marker)]
    tail = text[end:]
    return f"{head}\n{body}\n{tail}"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    module_path = root / "src" / "qchem_stack" / "chem" / "pre_quantum_docs_sync.py"
    spec = importlib.util.spec_from_file_location("pre_quantum_docs_sync", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module spec from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generated_pre_quantum_path_registry_markdown = module.generated_pre_quantum_path_registry_markdown
    generated_pre_quantum_source_table_markdown = module.generated_pre_quantum_source_table_markdown

    targets = [
        (
            root / "docs" / "技术文档_双线路经典输入与统一PreQuantumInput契约.md",
            "<!-- BEGIN:PRE_QUANTUM_SOURCE_TABLE -->",
            "<!-- END:PRE_QUANTUM_SOURCE_TABLE -->",
            generated_pre_quantum_source_table_markdown(),
        ),
        (
            root / "docs" / "pre_quantum_yaml_matrix.md",
            "<!-- BEGIN:PRE_QUANTUM_PATH_REGISTRY -->",
            "<!-- END:PRE_QUANTUM_PATH_REGISTRY -->",
            generated_pre_quantum_path_registry_markdown(),
        ),
    ]
    for path, start, end, body in targets:
        old = path.read_text(encoding="utf-8")
        new = _replace_block(old, start, end, body)
        path.write_text(new, encoding="utf-8")
    print("[ok] synced pre-quantum docs blocks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


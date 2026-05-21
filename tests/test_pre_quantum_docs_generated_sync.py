from __future__ import annotations

import importlib.util
from pathlib import Path


def _extract_block(text: str, start_marker: str, end_marker: str) -> str:
    start = text.find(start_marker)
    end = text.find(end_marker)
    assert start >= 0, f"missing marker: {start_marker}"
    assert end >= 0, f"missing marker: {end_marker}"
    assert end > start, f"marker order invalid: {start_marker} / {end_marker}"
    body = text[start + len(start_marker) : end]
    return body.strip()


def _load_docs_sync_module():  # type: ignore[no-untyped-def]
    root = Path(__file__).resolve().parents[1]
    module_path = root / "src" / "qchem_stack" / "chem" / "pre_quantum_docs_sync.py"
    spec = importlib.util.spec_from_file_location("pre_quantum_docs_sync", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_source_table_synced_in_contract_doc() -> None:
    root = Path(__file__).resolve().parents[1]
    module = _load_docs_sync_module()
    path = root / "docs" / "技术文档_双线路经典输入与统一PreQuantumInput契约.md"
    text = path.read_text(encoding="utf-8")
    actual = _extract_block(
        text,
        "<!-- BEGIN:PRE_QUANTUM_SOURCE_TABLE -->",
        "<!-- END:PRE_QUANTUM_SOURCE_TABLE -->",
    )
    assert actual == module.generated_pre_quantum_source_table_markdown()


def test_generated_path_registry_synced_in_yaml_matrix_doc() -> None:
    root = Path(__file__).resolve().parents[1]
    module = _load_docs_sync_module()
    path = root / "docs" / "pre_quantum_yaml_matrix.md"
    text = path.read_text(encoding="utf-8")
    actual = _extract_block(
        text,
        "<!-- BEGIN:PRE_QUANTUM_PATH_REGISTRY -->",
        "<!-- END:PRE_QUANTUM_PATH_REGISTRY -->",
    )
    assert actual == module.generated_pre_quantum_path_registry_markdown()

from __future__ import annotations

from qchem_stack.chem.pre_quantum_path import list_pre_quantum_path_sources
from tests.helpers.paths import docs_path


def test_pre_quantum_docs_cover_all_path_sources() -> None:
    docs = [
        docs_path("pre_quantum_yaml_matrix.md"),
        docs_path("技术文档_双线路经典输入与统一PreQuantumInput契约.md"),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in docs)
    missing = [source for source in list_pre_quantum_path_sources() if source not in combined]
    assert not missing, f"Pre-quantum path sources missing from docs: {missing}"

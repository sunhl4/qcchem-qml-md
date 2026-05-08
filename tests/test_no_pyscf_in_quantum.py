from __future__ import annotations

from pathlib import Path


def test_quantum_directory_has_no_pyscf_imports() -> None:
    root = Path(__file__).resolve().parents[1]
    quantum_dir = root / "src" / "qchem_stack" / "quantum"
    hits: list[str] = []
    for py in quantum_dir.rglob("*.py"):
        txt = py.read_text(encoding="utf-8")
        if "import pyscf" in txt or "from pyscf" in txt:
            hits.append(str(py.relative_to(root)))
    assert not hits, f"quantum layer must stay backend-agnostic; found pyscf imports in: {hits}"

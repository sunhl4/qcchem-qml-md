"""Quantum layer must not import orchestration or pyscf at module scope."""

from __future__ import annotations

import ast
from pathlib import Path


def _quantum_python_files() -> list[Path]:
    root = Path(__file__).resolve().parents[1] / "src" / "qchem_stack" / "quantum"
    return sorted(root.rglob("*.py"))


def _module_level_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def test_quantum_layer_has_no_orchestration_module_imports() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    forbidden_prefixes = ("qchem_stack.orchestration",)
    violations: list[str] = []
    for path in _quantum_python_files():
        rel = path.relative_to(repo_root)
        for mod in _module_level_imports(path):
            if mod.startswith(forbidden_prefixes):
                violations.append(f"{rel}: import {mod}")
    assert not violations, "module-scope imports violate quantum layer boundaries:\n" + "\n".join(
        violations
    )


def test_quantum_directory_has_no_pyscf_imports() -> None:
    root = Path(__file__).resolve().parents[1]
    quantum_dir = root / "src" / "qchem_stack" / "quantum"
    hits: list[str] = []
    for py in quantum_dir.rglob("*.py"):
        txt = py.read_text(encoding="utf-8")
        if "import pyscf" in txt or "from pyscf" in txt:
            hits.append(str(py.relative_to(root)))
    assert not hits, f"quantum layer must stay backend-agnostic; found pyscf imports in: {hits}"

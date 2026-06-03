"""DMET-related modules must not create chem -> integrations import cycles."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.paths import repo_root

_CHEM_DMET_FILES = [
    "src/qchem_stack/chem/embedding/dmet.py",
    "src/qchem_stack/chem/embedding/dmet_self_consistent.py",
    "src/qchem_stack/chem/embedding/schmidt_dmet_self_consistent.py",
]


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


def test_dmet_chem_modules_do_not_import_integrations_at_top_level() -> None:
    root = repo_root()
    offenders: list[str] = []
    for rel in _CHEM_DMET_FILES:
        imports = _module_level_imports(root / rel)
        for name in imports:
            if name.startswith("qchem_stack.integrations"):
                offenders.append(f"{rel}: {name}")
    assert offenders == []

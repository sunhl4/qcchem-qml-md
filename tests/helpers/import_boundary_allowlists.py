"""Shared import-boundary rules for CI script and layer boundary tests."""

from __future__ import annotations

import ast
from pathlib import Path

# Chem: lazy bridges documented in ENGINEERING_ARCHITECTURE / layer tests.
CHEM_LAZY_INTEGRATIONS_ALLOWLIST: frozenset[str] = frozenset(
    {
        "src/qchem_stack/chem/embedding/fragment_solvers/registry.py",
        "src/qchem_stack/chem/embedding/__init__.py",
    }
)

CHEM_LAZY_QUANTUM_ALLOWLIST: frozenset[str] = frozenset(
    {
        "src/qchem_stack/chem/embedding/fragment_solvers/qubit_hamiltonian_vqe.py",
    }
)

CHEM_FORBIDDEN_PREFIXES: tuple[str, ...] = (
    "qchem_stack.orchestration",
    "qchem_stack.jobs",
    "qchem_stack.quantum",
)

QUANTUM_FORBIDDEN_PREFIXES: tuple[str, ...] = (
    "qchem_stack.orchestration",
    "qchem_stack.jobs",
    "qchem_stack.integrations",
)

PYSCF_FORBIDDEN_PREFIXES: tuple[str, ...] = ("pyscf",)


def all_imports(path: Path) -> list[str]:
    """Every imported module name, including lazy/function-scope imports."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def module_level_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def _matches_prefix(mod: str, prefixes: tuple[str, ...]) -> bool:
    return any(mod == p or mod.startswith(f"{p}.") for p in prefixes)


def chem_import_violations(repo_root: Path) -> list[str]:
    chem_root = repo_root / "src" / "qchem_stack" / "chem"
    violations: list[str] = []
    for path in sorted(chem_root.rglob("*.py")):
        rel_posix = path.relative_to(repo_root).as_posix()
        for mod in all_imports(path):
            if _matches_prefix(mod, CHEM_FORBIDDEN_PREFIXES):
                if (
                    mod.startswith("qchem_stack.quantum")
                    and rel_posix in CHEM_LAZY_QUANTUM_ALLOWLIST
                ):
                    continue
                violations.append(f"{rel_posix}: import {mod}")
            if mod.startswith("qchem_stack.integrations"):
                module_level = set(module_level_imports(path))
                if mod in module_level:
                    violations.append(f"{rel_posix}: module-scope import {mod}")
                elif rel_posix not in CHEM_LAZY_INTEGRATIONS_ALLOWLIST:
                    violations.append(f"{rel_posix}: lazy import {mod}")
    return violations


def quantum_import_violations(repo_root: Path) -> list[str]:
    quantum_root = repo_root / "src" / "qchem_stack" / "quantum"
    violations: list[str] = []
    for path in sorted(quantum_root.rglob("*.py")):
        rel_posix = path.relative_to(repo_root).as_posix()
        for mod in all_imports(path):
            if _matches_prefix(mod, QUANTUM_FORBIDDEN_PREFIXES):
                violations.append(f"{rel_posix}: import {mod}")
            if _matches_prefix(mod, PYSCF_FORBIDDEN_PREFIXES):
                violations.append(f"{rel_posix}: import {mod}")
        txt = path.read_text(encoding="utf-8")
        if "import pyscf" in txt or "from pyscf" in txt:
            violations.append(f"{rel_posix}: pyscf import in source text")
    return violations


def collect_layer_violations(repo_root: Path) -> list[str]:
    return chem_import_violations(repo_root) + quantum_import_violations(repo_root)

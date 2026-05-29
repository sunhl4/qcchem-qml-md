"""Chem layer must not import orchestration, quantum, or integrations at module scope."""

from __future__ import annotations

import ast
from pathlib import Path

from tests.helpers.paths import repo_root


def _chem_python_files() -> list[Path]:
    root = repo_root() / "src" / "qchem_stack" / "chem"
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


def _all_imports(path: Path) -> list[str]:
    """Every imported module name, including lazy/function-scope imports (ast.walk).

    This mirrors ``scripts/check_import_layers.py`` so the test is as strict as
    the CI gate and cannot be bypassed by deferring an import into a function body.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


# Files allowed to import ``qchem_stack.integrations`` *lazily* (function scope
# only). These are deliberate plugin bridges (DMET fragment solvers / Schmidt
# per-fragment VQE) that would otherwise create a chem -> integrations -> chem
# import cycle. Any new lazy integrations import must be added here consciously.
_CHEM_LAZY_INTEGRATIONS_ALLOWLIST = {
    "src/qchem_stack/chem/embedding/fragment_solvers/registry.py",
    "src/qchem_stack/chem/embedding/__init__.py",
    "src/qchem_stack/chem/embedding/schmidt_variational_sidecar.py",
}


def test_chem_layer_never_imports_quantum_or_orchestration() -> None:
    """chem must not import quantum or orchestration anywhere, even lazily."""
    root = repo_root()
    forbidden_prefixes = ("qchem_stack.quantum", "qchem_stack.orchestration")
    violations: list[str] = []
    for path in _chem_python_files():
        rel = path.relative_to(root)
        for mod in _all_imports(path):
            if mod.startswith(forbidden_prefixes):
                violations.append(f"{rel}: import {mod}")
    assert not violations, "chem imports quantum/orchestration (forbidden):\n" + "\n".join(
        violations
    )


def test_chem_layer_integrations_imports_only_in_documented_allowlist() -> None:
    """integrations imports in chem are forbidden except documented lazy bridges."""
    root = repo_root()
    module_scope_violations: list[str] = []
    undocumented_lazy: list[str] = []
    for path in _chem_python_files():
        rel = path.relative_to(root).as_posix()
        module_level = {m for m in _module_level_imports(path)}
        all_mods = _all_imports(path)
        for mod in all_mods:
            if not mod.startswith("qchem_stack.integrations"):
                continue
            if mod in module_level:
                module_scope_violations.append(f"{rel}: module-scope import {mod}")
            elif rel not in _CHEM_LAZY_INTEGRATIONS_ALLOWLIST:
                undocumented_lazy.append(f"{rel}: lazy import {mod}")
    assert not module_scope_violations, (
        "chem must not import integrations at module scope:\n" + "\n".join(module_scope_violations)
    )
    assert not undocumented_lazy, (
        "new lazy chem -> integrations import; add to allowlist if intentional:\n"
        + "\n".join(undocumented_lazy)
    )


def test_kernels_lazy_export_run_nevpt2_casci() -> None:
    from qchem_stack.chem import kernels

    assert callable(kernels.run_nevpt2_casci)


def test_chem_root_lazy_exports_do_not_violate_import_boundaries() -> None:
    from qchem_stack.chem import (
        build_pre_quantum_input,
        capabilities_pyscf_production,
        classical_mean_field_via_solver_bridge,
        create_solver,
        registered_solver_ids,
        run_integration_checklist,
    )

    assert callable(classical_mean_field_via_solver_bridge)
    assert callable(create_solver)
    assert callable(build_pre_quantum_input)
    assert callable(registered_solver_ids)
    assert callable(run_integration_checklist)
    assert callable(capabilities_pyscf_production)

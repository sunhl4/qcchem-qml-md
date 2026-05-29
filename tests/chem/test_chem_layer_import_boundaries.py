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


def test_chem_layer_has_no_quantum_or_integrations_module_imports() -> None:
    root = repo_root()
    forbidden_prefixes = (
        "qchem_stack.quantum",
        "qchem_stack.integrations",
        "qchem_stack.orchestration",
    )
    violations: list[str] = []
    for path in _chem_python_files():
        rel = path.relative_to(root)
        for mod in _module_level_imports(path):
            if mod.startswith(forbidden_prefixes):
                violations.append(f"{rel}: import {mod}")
    assert not violations, "module-scope imports violate chem layer boundaries:\n" + "\n".join(
        violations
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

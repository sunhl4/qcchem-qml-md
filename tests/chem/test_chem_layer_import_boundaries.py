"""Chem layer must not import orchestration, quantum, or integrations at module scope."""

from __future__ import annotations

from tests.helpers.import_boundary_allowlists import chem_import_violations
from tests.helpers.paths import repo_root


def test_chem_layer_never_imports_quantum_or_orchestration() -> None:
    """chem must not import quantum, orchestration, or jobs (shared CI rules)."""
    violations = chem_import_violations(repo_root())
    quantum_orchestration = [
        v
        for v in violations
        if "qchem_stack.quantum" in v or "qchem_stack.orchestration" in v or "qchem_stack.jobs" in v
    ]
    assert not quantum_orchestration, (
        "chem imports quantum/orchestration/jobs (forbidden):\n" + "\n".join(quantum_orchestration)
    )


def test_chem_layer_integrations_imports_only_in_documented_allowlist() -> None:
    """integrations imports in chem are forbidden except documented lazy bridges."""
    violations = [v for v in chem_import_violations(repo_root()) if "integrations" in v]
    assert not violations, "chem integrations import boundary violated:\n" + "\n".join(violations)


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

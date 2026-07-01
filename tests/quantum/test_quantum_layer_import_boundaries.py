"""Quantum layer must not import orchestration or pyscf at module scope."""

from __future__ import annotations

from tests.helpers.import_boundary_allowlists import quantum_import_violations
from tests.helpers.paths import repo_root


def test_quantum_layer_never_imports_orchestration_or_integrations() -> None:
    """quantum must not import orchestration, integrations, or jobs (shared CI rules)."""
    violations = quantum_import_violations(repo_root())
    assert not violations, "imports violate quantum layer boundaries:\n" + "\n".join(violations)

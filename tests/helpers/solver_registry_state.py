"""Test-only helpers for isolating solver registry global state."""

from __future__ import annotations

import qchem_stack.chem.solvers.registry as solver_registry


def reset_solver_registry_state() -> None:
    """Reset module-level registry globals between tests."""
    with solver_registry._BOOTSTRAP_LOCK:
        solver_registry._REGISTRY.clear()
        solver_registry._BOOTSTRAPPED = False
        solver_registry._ENTRYPOINT_CONFLICT_POLICY = solver_registry.ENTRYPOINT_CONFLICT_WARN

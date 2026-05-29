# pyright: reportUnsupportedDunderAll=false
"""Pluggable classical integral / mean-field backends."""

from __future__ import annotations

from typing import Any

from qchem_stack.chem.solvers.adapter_contract import (
    SolverAdapterContractReport,
    validate_solver_adapter_contract,
)
from qchem_stack.chem.solvers.base import (
    ChemIntegralSolver,
    MolecularMeanFieldResult,
    SolverCapabilities,
)
from qchem_stack.chem.solvers.custom_solver_template import (
    CustomExternalIntegralSolver,
    build_stub_mean_field_result,
)
from qchem_stack.chem.solvers.mock_external_solver_example import (
    MockExternalIntegralSolver,
    register_mock_external_solver,
)
from qchem_stack.chem.solvers.registry import (
    InvalidSolverIdError,
    SolverRegistrationInfo,
    UnknownSolverError,
    create_solver,
    register_solver,
    registered_solver_ids,
    registered_solvers_detail,
    set_entrypoint_conflict_policy,
)

__all__ = [
    "ChemIntegralSolver",
    "CustomExternalIntegralSolver",
    "MockExternalIntegralSolver",
    "PrecomputedIntegralSolver",
    "MolecularMeanFieldResult",
    "InvalidSolverIdError",
    "SolverAdapterContractReport",
    "SolverRegistrationInfo",
    "SolverCapabilities",
    "UnknownSolverError",
    "build_stub_mean_field_result",
    "create_solver",
    "register_mock_external_solver",
    "register_solver",
    "registered_solver_ids",
    "registered_solvers_detail",
    "set_entrypoint_conflict_policy",
    "validate_solver_adapter_contract",
]


def __getattr__(name: str) -> Any:
    if name == "PrecomputedIntegralSolver":
        from qchem_stack.chem.solvers.precomputed_solver import PrecomputedIntegralSolver

        return PrecomputedIntegralSolver
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

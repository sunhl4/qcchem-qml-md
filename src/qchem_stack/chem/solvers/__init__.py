"""Pluggable classical integral / mean-field backends (Tangelo-style ``IntegralSolver`` analog)."""

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
from qchem_stack.chem.solvers.registry import create_solver, register_solver, registered_solver_ids

__all__ = [
    "ChemIntegralSolver",
    "CustomExternalIntegralSolver",
    "MockExternalIntegralSolver",
    "MolecularMeanFieldResult",
    "SolverAdapterContractReport",
    "SolverCapabilities",
    "build_stub_mean_field_result",
    "create_solver",
    "register_mock_external_solver",
    "register_solver",
    "registered_solver_ids",
    "validate_solver_adapter_contract",
]

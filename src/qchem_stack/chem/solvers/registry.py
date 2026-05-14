"""Solver registry: **pluggable classical chemistry backends** for `scf.driver`.

`pyscf` / `psi4` are **registered adapters**, not architectural singletons.
Orchestration must obtain mean-field data via :func:`create_solver` →
:class:`~qchem_stack.chem.solvers.base.ChemIntegralSolver` →
:class:`~qchem_stack.chem.solvers.base.MolecularMeanFieldResult` (see
:func:`~qchem_stack.chem.bridges.facade.classical_mean_field_via_solver_bridge`).
Downstream quantum/embedding stages must **not** assume PySCF beyond what
:attr:`~qchem_stack.chem.solvers.base.SolverCapabilities` declares.
"""

from __future__ import annotations

from collections.abc import Callable

from qchem_stack.chem.solvers.base import ChemIntegralSolver
from qchem_stack.config import ExperimentConfig

SolverFactory = Callable[[ExperimentConfig], ChemIntegralSolver]

_FACTORIES: dict[str, SolverFactory] = {}
_BOOTSTRAPPED = False


def register_solver(name: str, factory: SolverFactory) -> None:
    key = name.strip().lower()
    if not key:
        raise ValueError("solver name must be non-empty")
    _FACTORIES[key] = factory


def registered_solver_ids() -> frozenset[str]:
    _ensure_bootstrap()
    return frozenset(_FACTORIES.keys())


def _ensure_bootstrap() -> None:
    global _BOOTSTRAPPED
    if _BOOTSTRAPPED:
        return
    from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver

    register_solver("pyscf", PySCFIntegralSolver.from_experiment_config)
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver

    register_solver("psi4", Psi4IntegralSolver.from_experiment_config)
    _BOOTSTRAPPED = True


def create_solver(cfg: ExperimentConfig) -> ChemIntegralSolver:
    """Instantiate backend from ``scf.driver``."""
    _ensure_bootstrap()
    key = cfg.scf.driver.strip().lower()
    if key not in _FACTORIES:
        raise ValueError(f"Unknown scf.driver={cfg.scf.driver!r}. Registered: {sorted(_FACTORIES)}")
    return _FACTORIES[key](cfg)

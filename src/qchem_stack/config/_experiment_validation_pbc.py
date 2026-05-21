"""PBC-related cross-field validation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.exceptions import ConfigurationError

if TYPE_CHECKING:
    from .experiment import ExperimentConfig


def validate_pbc_k_mesh_solver_capability(spec: ExperimentConfig) -> None:
    pbc = spec.chemistry_extended.pbc
    if pbc.cell_vectors_bohr is None:
        return
    mesh = list(pbc.kpoint_mesh or [1, 1, 1])
    if not mesh or max(mesh) <= 1:
        return
    from qchem_stack.chem.solvers.registry import create_solver

    caps = create_solver(spec).capabilities
    if not caps.supports_pbc_k_mesh:
        raise ConfigurationError(
            "Periodic Monkhorst–Pack mesh with max(pbc.kpoint_mesh)>1 requires "
            "SolverCapabilities.supports_pbc_k_mesh=True on the selected backend "
            f"(scf.driver={spec.scf.driver!r}). Use scf.driver='pyscf' or set "
            "chemistry_extended.pbc.kpoint_mesh to [1, 1, 1] for Gamma-only drivers. "
            "See docs/execution/multi_backend_integration_philosophy.md."
        )


def validate_pbc_excludes_casscf_hooks(spec: ExperimentConfig) -> None:
    ce = spec.chemistry_extended
    pbc = ce.pbc
    mesh = list(pbc.kpoint_mesh or [1, 1, 1])
    pbc_on = bool(pbc.cell_vectors_bohr) or mesh != [1, 1, 1]
    if not pbc_on:
        return
    if spec.active_space.strategy == "avas":
        raise ConfigurationError(
            "active_space.strategy='avas' is unsupported with periodic boundary conditions."
        )
    if ce.casscf.orbital_optimization_audit:
        raise ConfigurationError(
            "chemistry_extended.casscf.orbital_optimization_audit is unsupported with PBC in this milestone."
        )
    if ce.casscf.orbital_optimization_for_integrals:
        raise ConfigurationError(
            "chemistry_extended.casscf.orbital_optimization_for_integrals is unsupported with PBC "
            "in this milestone."
        )

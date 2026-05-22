# pyright: reportUnsupportedDunderAll=false
"""Classical chemistry: solver registry, bridge interchange, and pre-quantum assembly.

**Errors**

- :exc:`qchem_stack.chem.solvers.registry.UnknownSolverError`: ``scf.driver`` id is not
  registered (see :func:`registered_solver_ids`).
- :exc:`qchem_stack.chem.solvers.registry.InvalidSolverIdError`: malformed solver id string.
- ``ValueError``: unsupported backend capability for the requested pre-quantum path,
  non-RHF reference for restricted active-space builds, or invalid active-space sizes.
- ``ImportError`` / optional dependency errors: PySCF/Psi4 not installed when the selected
  solver requires them.

**Preferred entry points (new code)**

1. :func:`create_solver` → ``ChemIntegralSolver.compute_mean_field``
2. :func:`classical_mean_field_reference_from_config` / :func:`pyscf_rhf_result_from_config`
3. :func:`build_pre_quantum_input` (orchestration-facing handoff)
4. :func:`restricted_active_space_quantum_problem_from_config` (PySCF ``get_system`` analog)
5. :func:`pyscf_ao_system_from_config` (AO / Löwdin views without :class:`~qchem_stack.chem.drivers.pyscf_driver.PySCFDriver`)

Layout: submodules by area (:mod:`solvers`, :mod:`bridges`, :mod:`integrals`, :mod:`embedding`,
:mod:`active_space`, :mod:`systems`, :mod:`classical_benchmarks`). Import names from
``qchem_stack.chem`` for the supported public surface; see
:mod:`qchem_stack.chem.drivers` only for deprecated PySCF driver shims.

Package index: ``src/qchem_stack/chem/README.md``. Style standard:
``docs/chem_模块风格约定.md``.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.jordan_wigner_sparse import jordan_wigner_interaction_operator_sparse
from qchem_stack.chem.restricted_integral_operator import (
    RestrictedActiveSpaceIntegralOperatorCompact,
)
from qchem_stack.chem.spatial_restricted_fermion import (
    restricted_spatial_integrals_to_fermion_operator,
)
from qchem_stack.chem.system import MolecularSystem, ReferenceState

__all__ = [
    "ClassicalBenchmarkContext",
    "ClassicalMeanFieldReference",
    "FermionQubitMappingName",
    "FermionSpace",
    "IntegrationChecklistReport",
    "MolecularSystem",
    "QubitHamiltonian",
    "ReferenceState",
    "RestrictedActiveSpaceIntegralOperatorCompact",
    "RestrictedActiveSpaceQuantumProblem",
    "build_pre_quantum_input",
    "capabilities_precomputed_offline",
    "capabilities_psi4_production",
    "capabilities_pyscf_production",
    "classical_mean_field_reference_from_config",
    "classical_mean_field_via_solver_bridge",
    "create_solver",
    "fork_driver_meta",
    "jordan_wigner_interaction_operator_sparse",
    "molecular_system_from_experiment",
    "pyscf_ao_system_from_config",
    "pyscf_ao_system_from_rhf",
    "pyscf_lowdin_system_from_rhf",
    "pyscf_rhf_result_from_config",
    "registered_solver_ids",
    "restricted_active_space_quantum_problem_from_config",
    "restricted_spatial_integrals_to_fermion_operator",
    "run_classical_post_hf_benchmarks",
    "run_integration_checklist",
]

_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "ClassicalBenchmarkContext": (
        "qchem_stack.chem.classical_benchmarks",
        "ClassicalBenchmarkContext",
    ),
    "ClassicalMeanFieldReference": (
        "qchem_stack.chem.bridges.mean_field_reference",
        "ClassicalMeanFieldReference",
    ),
    "FermionQubitMappingName": (
        "qchem_stack.chem.hamiltonian_meta",
        "FermionQubitMappingName",
    ),
    "QubitHamiltonian": (
        "qchem_stack.chem.hamiltonian",
        "QubitHamiltonian",
    ),
    "RestrictedActiveSpaceQuantumProblem": (
        "qchem_stack.chem.molecular_problem",
        "RestrictedActiveSpaceQuantumProblem",
    ),
    "build_pre_quantum_input": (
        "qchem_stack.chem.pre_quantum_build",
        "build_pre_quantum_input",
    ),
    "classical_mean_field_reference_from_config": (
        "qchem_stack.chem.bridges.reference_factory",
        "classical_mean_field_reference_from_config",
    ),
    "classical_mean_field_via_solver_bridge": (
        "qchem_stack.chem.bridges.facade",
        "classical_mean_field_via_solver_bridge",
    ),
    "create_solver": (
        "qchem_stack.chem.solvers.registry",
        "create_solver",
    ),
    "fork_driver_meta": (
        "qchem_stack.chem.bridges.driver_meta",
        "fork_driver_meta",
    ),
    "molecular_system_from_experiment": (
        "qchem_stack.chem.molecular_system_config",
        "molecular_system_from_experiment",
    ),
    "pyscf_ao_system_from_config": (
        "qchem_stack.chem.systems.pyscf_factory",
        "pyscf_ao_system_from_config",
    ),
    "pyscf_ao_system_from_rhf": (
        "qchem_stack.chem.systems.pyscf_factory",
        "pyscf_ao_system_from_rhf",
    ),
    "pyscf_lowdin_system_from_rhf": (
        "qchem_stack.chem.systems.pyscf_factory",
        "pyscf_lowdin_system_from_rhf",
    ),
    "pyscf_rhf_result_from_config": (
        "qchem_stack.chem.bridges.reference_factory",
        "pyscf_rhf_result_from_config",
    ),
    "registered_solver_ids": (
        "qchem_stack.chem.solvers.registry",
        "registered_solver_ids",
    ),
    "restricted_active_space_quantum_problem_from_config": (
        "qchem_stack.chem.molecular_problem_build",
        "restricted_active_space_quantum_problem_from_config",
    ),
    "run_classical_post_hf_benchmarks": (
        "qchem_stack.chem.classical_benchmarks",
        "run_classical_post_hf_benchmarks",
    ),
    "run_integration_checklist": (
        "qchem_stack.chem.integration.checklist",
        "run_integration_checklist",
    ),
    "IntegrationChecklistReport": (
        "qchem_stack.chem.integration.checklist",
        "IntegrationChecklistReport",
    ),
    "capabilities_pyscf_production": (
        "qchem_stack.chem.integration.presets",
        "capabilities_pyscf_production",
    ),
    "capabilities_psi4_production": (
        "qchem_stack.chem.integration.presets",
        "capabilities_psi4_production",
    ),
    "capabilities_precomputed_offline": (
        "qchem_stack.chem.integration.presets",
        "capabilities_precomputed_offline",
    ),
}


def __getattr__(name: str) -> Any:
    target = _LAZY_ATTRS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value

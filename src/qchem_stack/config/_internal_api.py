"""Internal configuration API for orchestration and pipeline integration.

This module provides validation, conversion, and helper functions used by the
orchestration layer, job system, and other internal modules. Application code
should typically not import from here directly.

Typical usage (internal)::

    from qchem_stack.config._internal_api import (
        validate_experiment_for_run,
        backend_spec_from_config,
        compiler_pass_bundle_from_config,
    )

    validate_experiment_for_run(cfg, backend_caps)
    spec = backend_spec_from_config(cfg)
"""

from __future__ import annotations

from ._constants import ANGSTROM_TO_BOHR, MD_ML_MAX_EXTRA_GEOMETRIES
from ._embedding_validation import SCHMIDT_DMET_MAX_CYCLES_LIMIT
from ._experiment_validation import validate_experiment_for_run, validate_pre_quantum_contract
from ._pre_quantum_path import PreQuantumPath, resolve_pre_quantum_path
from .active_space_helpers import (
    resolve_fermion_qubit_mapping,
    resolve_n_electrons,
    resolve_n_orbitals,
)
from .chemistry_extended_helpers import avas_ao_labels, pbc_cell_vectors_bohr
from .geometry_files import (
    load_cartesian_geometry_file,
    merge_molecule_dict_from_geometry_file,
    parse_xyz,
    preprocess_experiment_dict_geometry_files,
)
from .io import (
    backend_spec_from_config,
    compiler_bundle_signature_from_config,
    compiler_pass_bundle_from_config,
)
from .md_ml_export_helpers import extra_coordinates_bohr, trajectory_theory_level
from .mitigation_helpers import mitigation_repro_core_fields, pmsv_enabled, zne_enabled
from .quantum_graph import ComputableGraphEdgeDecl, ComputableGraphEdgeRemove
from .quantum_helpers import (
    classify_pauli_expectation_path_for_config,
    pauli_protocol_enabled,
    quantum_repro_core_fields,
    quantum_repro_sidecar_fields,
)
from .scf_helpers import resolve_scf_density_fit, resolve_scf_max_cycle

__all__ = [
    "ANGSTROM_TO_BOHR",
    "ComputableGraphEdgeDecl",
    "ComputableGraphEdgeRemove",
    "MD_ML_MAX_EXTRA_GEOMETRIES",
    "PreQuantumPath",
    "SCHMIDT_DMET_MAX_CYCLES_LIMIT",
    "avas_ao_labels",
    "backend_spec_from_config",
    "classify_pauli_expectation_path_for_config",
    "compiler_bundle_signature_from_config",
    "compiler_pass_bundle_from_config",
    "extra_coordinates_bohr",
    "load_cartesian_geometry_file",
    "merge_molecule_dict_from_geometry_file",
    "mitigation_repro_core_fields",
    "parse_xyz",
    "pauli_protocol_enabled",
    "pbc_cell_vectors_bohr",
    "pmsv_enabled",
    "preprocess_experiment_dict_geometry_files",
    "quantum_repro_core_fields",
    "quantum_repro_sidecar_fields",
    "resolve_fermion_qubit_mapping",
    "resolve_n_electrons",
    "resolve_n_orbitals",
    "resolve_pre_quantum_path",
    "resolve_scf_density_fit",
    "resolve_scf_max_cycle",
    "trajectory_theory_level",
    "validate_experiment_for_run",
    "validate_pre_quantum_contract",
    "zne_enabled",
]

"""Experiment configuration models and YAML I/O.

**Errors**

- ``pydantic.ValidationError``: invalid field values, cross-field constraints, or bad types when
  building an :class:`ExperimentConfig` (e.g. ``ExperimentConfig.model_validate``,
  ``ExperimentConfig.from_yaml_dict``). Prefer this for programmatic fixes with field paths.
- :exc:`qchem_stack.exceptions.ConfigurationError`: experiment YAML file missing or unreadable,
  YAML that is not a mapping after parse, missing geometry files referenced by
  ``molecule.geometry_file``, or dependency gaps surfaced from config (e.g. z-matrix
  without PySCF via :meth:`MoleculeSpec.coordinates_in_bohr`).

Layout: submodules by area (:mod:`molecule`, :mod:`geometry_files`, :mod:`scf`, :mod:`active_space`, :mod:`quantum`,
:mod:`embedding`, ...). Import names from ``qchem_stack.config`` for the supported public surface.
"""

from __future__ import annotations

from ._constants import ANGSTROM_TO_BOHR, MD_ML_MAX_EXTRA_GEOMETRIES
from ._embedding_validation import SCHMIDT_DMET_MAX_CYCLES_LIMIT
from ._experiment_validation import validate_experiment_for_run, validate_pre_quantum_contract
from ._pre_quantum_path import PreQuantumPath, resolve_pre_quantum_path
from .active_space import ActiveSpaceSpec
from .active_space_helpers import (
    resolve_fermion_qubit_mapping,
    resolve_n_electrons,
    resolve_n_orbitals,
)
from .backend import BackendSpecConfig
from .chemistry_extended import ChemistryExtendedSpec
from .chemistry_extended_helpers import avas_ao_labels, pbc_cell_vectors_bohr
from .compiler import CompilerSpec
from .embedding import EmbeddingSpec
from .experiment import ExperimentConfig
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
    dump_experiment_config,
    load_experiment_config,
)
from .md_ml_export import MdMlExportSpec
from .md_ml_export_helpers import extra_coordinates_bohr, trajectory_theory_level
from .mitigation import MitigationSpec
from .mitigation_helpers import mitigation_repro_core_fields, pmsv_enabled, zne_enabled
from .molecule import MoleculeSpec
from .nexus import NexusAnalogSpec, NexusCloudSpec
from .parity_integrations import ParityIntegrationsSpec
from .quantum import QuantumSpec
from .quantum_enums import OperatorPoolId
from .quantum_graph import ComputableGraphEdgeDecl, ComputableGraphEdgeRemove
from .quantum_helpers import (
    classify_pauli_expectation_path_for_config,
    pauli_protocol_enabled,
    quantum_repro_core_fields,
    quantum_repro_sidecar_fields,
)
from .scf import SCFSpec
from .scf_helpers import resolve_scf_density_fit, resolve_scf_max_cycle

__all__ = [
    "ANGSTROM_TO_BOHR",
    "ActiveSpaceSpec",
    "BackendSpecConfig",
    "ChemistryExtendedSpec",
    "CompilerSpec",
    "ComputableGraphEdgeDecl",
    "ComputableGraphEdgeRemove",
    "MD_ML_MAX_EXTRA_GEOMETRIES",
    "OperatorPoolId",
    "EmbeddingSpec",
    "ExperimentConfig",
    "MdMlExportSpec",
    "MitigationSpec",
    "MoleculeSpec",
    "NexusAnalogSpec",
    "NexusCloudSpec",
    "ParityIntegrationsSpec",
    "PreQuantumPath",
    "QuantumSpec",
    "SCFSpec",
    "SCHMIDT_DMET_MAX_CYCLES_LIMIT",
    "backend_spec_from_config",
    "classify_pauli_expectation_path_for_config",
    "compiler_bundle_signature_from_config",
    "compiler_pass_bundle_from_config",
    "dump_experiment_config",
    "load_experiment_config",
    "load_cartesian_geometry_file",
    "merge_molecule_dict_from_geometry_file",
    "parse_xyz",
    "preprocess_experiment_dict_geometry_files",
    "avas_ao_labels",
    "extra_coordinates_bohr",
    "mitigation_repro_core_fields",
    "pbc_cell_vectors_bohr",
    "pmsv_enabled",
    "pauli_protocol_enabled",
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

ExperimentConfig.model_rebuild()

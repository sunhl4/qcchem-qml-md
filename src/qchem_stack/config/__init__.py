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

from ._constants import ANGSTROM_TO_BOHR
from ._experiment_validation import (
    SCHMIDT_DMET_MAX_CYCLES_LIMIT,
    validate_pre_quantum_contract,
)
from .active_space import ActiveSpaceSpec
from .backend import BackendSpecConfig
from .chemistry_extended import ChemistryExtendedSpec
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
from .mitigation import MitigationSpec
from .molecule import MoleculeSpec
from .nexus import NexusAnalogSpec, NexusCloudSpec
from .parity_integrations import ParityIntegrationsSpec
from .quantum import ComputableGraphEdgeDecl, ComputableGraphEdgeRemove, QuantumSpec
from .scf import SCFSpec

__all__ = [
    "ANGSTROM_TO_BOHR",
    "ActiveSpaceSpec",
    "BackendSpecConfig",
    "ChemistryExtendedSpec",
    "CompilerSpec",
    "ComputableGraphEdgeDecl",
    "ComputableGraphEdgeRemove",
    "EmbeddingSpec",
    "ExperimentConfig",
    "MdMlExportSpec",
    "MitigationSpec",
    "MoleculeSpec",
    "NexusAnalogSpec",
    "NexusCloudSpec",
    "ParityIntegrationsSpec",
    "QuantumSpec",
    "SCFSpec",
    "SCHMIDT_DMET_MAX_CYCLES_LIMIT",
    "backend_spec_from_config",
    "compiler_bundle_signature_from_config",
    "compiler_pass_bundle_from_config",
    "dump_experiment_config",
    "load_experiment_config",
    "load_cartesian_geometry_file",
    "merge_molecule_dict_from_geometry_file",
    "parse_xyz",
    "preprocess_experiment_dict_geometry_files",
    "validate_pre_quantum_contract",
]

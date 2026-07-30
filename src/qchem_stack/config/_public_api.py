"""User-facing configuration API.

This module provides the primary configuration classes and I/O functions that
users need to define, load, and save experiment configurations. Import from
here for application-level code.

Typical usage::

    from qchem_stack.config._public_api import (
        ExperimentConfig,
        MoleculeSpec,
        QuantumSpec,
        load_experiment_config,
        dump_experiment_config,
    )

    cfg = load_experiment_config("h2.yaml")
    # ... modify cfg ...
    dump_experiment_config(cfg, "h2_modified.yaml")
"""

from __future__ import annotations

from .active_space import ActiveSpaceSpec
from .backend import BackendSpecConfig
from .chemistry_extended import ChemistryExtendedSpec
from .compiler import CompilerSpec
from .embedding import EmbeddingSpec
from .experiment import ExperimentConfig
from .gqe import GqeSpec
from .io import dump_experiment_config, load_experiment_config
from .md_ml_export import MdMlExportSpec
from .mitigation import MitigationSpec
from .molecule import MoleculeSpec
from .nexus import NexusAnalogSpec, NexusCloudSpec
from .parity_integrations import ParityIntegrationsSpec
from .quantum import QuantumSpec
from .quantum_enums import OperatorPoolId
from .scf import SCFSpec

__all__ = [
    "ActiveSpaceSpec",
    "BackendSpecConfig",
    "ChemistryExtendedSpec",
    "CompilerSpec",
    "EmbeddingSpec",
    "ExperimentConfig",
    "GqeSpec",
    "MdMlExportSpec",
    "MitigationSpec",
    "MoleculeSpec",
    "NexusAnalogSpec",
    "NexusCloudSpec",
    "OperatorPoolId",
    "ParityIntegrationsSpec",
    "QuantumSpec",
    "SCFSpec",
    "dump_experiment_config",
    "load_experiment_config",
]

ExperimentConfig.model_rebuild()

"""Top-level experiment config model and cross-section validation guards.

`ExperimentConfig` is the single schema source for YAML-backed experiments.
Unknown top-level YAML keys are preserved under `extra` to keep integrations
forward-compatible without relaxing strict typed fields.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from ._experiment_validation import (
    preprocess_precomputed_bundle_path,
    preprocess_top_level_yaml_dict,
    validate_avas_strategy_requires_pyscf_labels,
    validate_embedding_atom_indices_within_molecule,
    validate_md_ml_extra_coordinates_shape,
    validate_md_ml_pauli_energy_requires_pauli_protocol,
    validate_uccsd_variational_constraints,
)
from .active_space import ActiveSpaceSpec
from .backend import BackendSpecConfig
from .chemistry_extended import ChemistryExtendedSpec
from .compiler import CompilerSpec
from .embedding import EmbeddingSpec
from .geometry_files import preprocess_experiment_dict_geometry_files
from .md_ml_export import MdMlExportSpec
from .mitigation import MitigationSpec
from .molecule import MoleculeSpec
from .nexus import NexusAnalogSpec, NexusCloudSpec
from .parity_integrations import ParityIntegrationsSpec
from .quantum import QuantumSpec
from .scf import SCFSpec


class ExperimentConfig(BaseModel):
    """Validated experiment contract spanning chemistry, backend, and algorithm specs."""

    schema_version: str = "1"
    experiment_id: str
    random_seed: int = 0
    molecule: MoleculeSpec
    scf: SCFSpec = Field(default_factory=SCFSpec)
    active_space: ActiveSpaceSpec
    backend: BackendSpecConfig = Field(default_factory=BackendSpecConfig)
    mitigation: MitigationSpec = Field(default_factory=MitigationSpec)
    compiler: CompilerSpec = Field(default_factory=CompilerSpec)
    quantum: QuantumSpec = Field(default_factory=QuantumSpec)
    embedding: EmbeddingSpec = Field(default_factory=EmbeddingSpec)
    chemistry_extended: ChemistryExtendedSpec = Field(default_factory=ChemistryExtendedSpec)
    nexus_analog: NexusAnalogSpec = Field(default_factory=NexusAnalogSpec)
    nexus_cloud: NexusCloudSpec = Field(default_factory=NexusCloudSpec)
    parity_integrations: ParityIntegrationsSpec = Field(default_factory=ParityIntegrationsSpec)
    md_ml_export: MdMlExportSpec = Field(default_factory=MdMlExportSpec)
    extra: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_yaml_dict(
        cls,
        data: Mapping[str, Any],
        *,
        geometry_files_base_dir: Path | str | None = None,
    ) -> ExperimentConfig:
        top_level = preprocess_top_level_yaml_dict(data, known_fields=set(cls.model_fields))
        if geometry_files_base_dir is not None:
            preprocess_experiment_dict_geometry_files(
                top_level, base_dir=Path(geometry_files_base_dir)
            )
            preprocess_precomputed_bundle_path(top_level, base_dir=Path(geometry_files_base_dir))
        return cls.model_validate(top_level)

    @model_validator(mode="after")
    def _embedding_atom_indices_within_molecule(self) -> ExperimentConfig:
        validate_embedding_atom_indices_within_molecule(self)
        return self

    @model_validator(mode="after")
    def _md_ml_extra_coordinates_shape(self) -> ExperimentConfig:
        validate_md_ml_extra_coordinates_shape(self)
        return self

    @model_validator(mode="after")
    def _md_ml_pauli_energy_requires_pauli_protocol(self) -> ExperimentConfig:
        validate_md_ml_pauli_energy_requires_pauli_protocol(self)
        return self

    @model_validator(mode="after")
    def _avas_strategy_requires_pyscf_labels(self) -> ExperimentConfig:
        validate_avas_strategy_requires_pyscf_labels(self)
        return self

    @model_validator(mode="after")
    def _uccsd_variational_constraints(self) -> ExperimentConfig:
        validate_uccsd_variational_constraints(self)
        return self

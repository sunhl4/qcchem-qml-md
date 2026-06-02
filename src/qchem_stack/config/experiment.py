"""Top-level experiment config model and cross-section validation guards.

`ExperimentConfig` is the single schema source for YAML-backed experiments.
Unknown top-level YAML keys are preserved under `extra` to keep integrations
forward-compatible without relaxing strict typed fields.

**YAML load chain** (see also ``docs/config_校验分层约定.md``):

1. ``preprocess_top_level_yaml_dict`` — merge unknown top-level keys into ``extra``.
2. Geometry / precomputed path preprocess when ``from_yaml_dict(..., geometry_files_base_dir=...)``.
3. Pydantic section models (nested blocks use ``extra='forbid'``).
4. ``ExperimentConfig`` cross-section ``@model_validator`` registry.
5. Optional ``validate_pre_quantum_contract()`` at pipeline entry (subset of step 4;
   does **not** include ``validate_pbc_k_mesh_solver_capability``).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, field_validator, model_validator

from ._experiment_validation import (
    EXPERIMENT_CROSS_VALIDATORS,
    preprocess_precomputed_bundle_path,
    preprocess_top_level_yaml_dict,
)
from .backend import BackendSpecConfig
from .chemistry_extended import ChemistryExtendedSpec
from .compiler import CompilerSpec
from .embedding_specs import EmbeddingNone
from .geometry_files import preprocess_experiment_dict_geometry_files
from .md_ml_export import MdMlExportSpec
from .mitigation import MitigationSpec
from .nexus import NexusAnalogSpec, NexusCloudSpec
from .parity_integrations import ParityIntegrationsSpec
from .quantum import QuantumSpec
from .scf import SCFSpec

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .active_space import ActiveSpaceSpec
    from .embedding import EmbeddingSpec
    from .molecule import MoleculeSpec


class CoreExperimentConfig(BaseModel):
    """Essential experiment configuration with the 6 core fields.

    This provides a minimal configuration surface for users who only need
    the essential fields: experiment identity, molecular system, active space,
    and the three main execution layers (SCF, quantum, backend).

    For full configuration with all optional features (embedding, mitigation,
    extended chemistry, etc.), use :class:`ExperimentConfig` which inherits
    from this class.
    """

    experiment_id: str
    molecule: MoleculeSpec
    active_space: ActiveSpaceSpec
    scf: SCFSpec = Field(default_factory=SCFSpec)
    quantum: QuantumSpec = Field(default_factory=QuantumSpec)
    backend: BackendSpecConfig = Field(default_factory=BackendSpecConfig)


class ExperimentConfig(CoreExperimentConfig):
    """Validated experiment contract spanning chemistry, backend, and algorithm specs.

    Inherits from :class:`CoreExperimentConfig` and adds 11 optional fields for
    advanced features: embedding, mitigation, extended chemistry, cloud integrations,
    and more.
    """

    schema_version: str = Field(
        default="2",
        description='Experiment schema generation; nested YAML requires "2".',
    )
    random_seed: int = 0
    mitigation: MitigationSpec = Field(default_factory=MitigationSpec)
    compiler: CompilerSpec = Field(default_factory=CompilerSpec)
    embedding: EmbeddingSpec = Field(default_factory=EmbeddingNone)
    chemistry_extended: ChemistryExtendedSpec = Field(default_factory=ChemistryExtendedSpec)
    nexus_analog: NexusAnalogSpec = Field(default_factory=NexusAnalogSpec)
    nexus_cloud: NexusCloudSpec = Field(default_factory=NexusCloudSpec)
    parity_integrations: ParityIntegrationsSpec = Field(default_factory=ParityIntegrationsSpec)
    md_ml_export: MdMlExportSpec = Field(default_factory=MdMlExportSpec)
    extra: dict[str, Any] = Field(default_factory=dict)

    @field_validator("schema_version")
    @classmethod
    def _require_nested_schema_version(cls, v: str) -> str:
        if str(v).strip() != "2":
            raise ValueError(
                f'schema_version must be "2" (nested YAML); got {v!r}. '
                "Rewrite the config to nested blocks (see docs/config_校验分层约定.md)."
            )
        return "2"

    @classmethod
    def from_yaml_dict(
        cls,
        data: Mapping[str, Any],
        *,
        geometry_files_base_dir: Path | str | None = None,
        strict_top_level_keys: bool = False,
    ) -> ExperimentConfig:
        top_level = preprocess_top_level_yaml_dict(
            data,
            known_fields=set(cls.model_fields),
            strict_unknown_top_level=strict_top_level_keys,
        )
        if geometry_files_base_dir is not None:
            preprocess_experiment_dict_geometry_files(
                top_level, base_dir=Path(geometry_files_base_dir)
            )
            preprocess_precomputed_bundle_path(top_level, base_dir=Path(geometry_files_base_dir))
        return cls.model_validate(top_level)

    @model_validator(mode="after")
    def _cross_section_contract(self) -> ExperimentConfig:
        for validator in EXPERIMENT_CROSS_VALIDATORS:
            validator(self)
        return self

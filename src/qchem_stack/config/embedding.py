"""Embedding configuration for DMET/projection workflows and plugin hooks.

Field reference: ``docs/说明_embedding配置.md``.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from .embedding_enums import (
    DmetHamiltonianSource,
    EmbeddingInputRepresentation,
    EmbeddingMode,
    ProjectionQuantumHamiltonian,
)
from .embedding_specs import (
    DmetEmbeddingSpec,
    DmetFragmentSolverSpec,
    EmbeddingBase,
    EmbeddingDmet,
    EmbeddingNone,
    EmbeddingPlugin,
    EmbeddingProjection,
    PluginEmbeddingSpec,
    ProjectionEmbeddingSpec,
    SchmidtEmbeddingSpec,
)

EmbeddingSpec = Annotated[
    EmbeddingNone | EmbeddingDmet | EmbeddingProjection | EmbeddingPlugin,
    Field(discriminator="mode"),
]

__all__ = [
    "DmetEmbeddingSpec",
    "DmetFragmentSolverSpec",
    "DmetHamiltonianSource",
    "EmbeddingBase",
    "EmbeddingDmet",
    "EmbeddingInputRepresentation",
    "EmbeddingMode",
    "EmbeddingNone",
    "EmbeddingPlugin",
    "EmbeddingProjection",
    "EmbeddingSpec",
    "PluginEmbeddingSpec",
    "ProjectionEmbeddingSpec",
    "ProjectionQuantumHamiltonian",
    "SchmidtEmbeddingSpec",
]

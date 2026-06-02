"""Nested embedding sub-schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, field_validator, model_validator

from qchem_stack.quantum.algorithms.tolerances import (
    PROJECTION_EMBEDDING_THRESHOLD,
    RIDGE_REGULARIZATION,
)

from ._base import ForbidExtraBase
from ._validation import strip_optional_text
from .embedding_enums import (
    DmetHamiltonianSource,
    EmbeddingInputRepresentation,
    EmbeddingMode,
    ProjectionQuantumHamiltonian,
)


class DmetFragmentSolverSpec(ForbidExtraBase):
    plugin_id: str | None = Field(
        default=None,
        description="Fragment solver plugin id (see chem.embedding.fragment_solvers.registry).",
    )
    use_exact: bool = Field(
        default=False, description="Dense ED impurity solve for small n_qubits."
    )
    exact_max_qubits: int = Field(
        default=14, ge=1, le=64, description="Skip dense ED above this count."
    )


class SchmidtEmbeddingSpec(ForbidExtraBase):
    fragment_atom_indices: list[int] = Field(default_factory=list)
    multi_fragment_atom_groups: list[list[int]] = Field(default_factory=list)
    multi_primary_fragment_index: int = Field(default=0, ge=0)
    n_bath_spatial: int = Field(default=2, ge=1)
    max_impurity_spatial_orbitals: int = Field(default=14, ge=2)
    run_mu_bisection: bool = False
    attach_fci_reference: bool = True
    fci_reference_max_spatial_orbitals: int = 8
    dmet_max_cycles: int = Field(default=1, ge=1, le=256)
    dmet_mixing_alpha: float = Field(default=0.35, gt=0.0, le=1.0)
    dmet_convergence_tol: float = Field(default=RIDGE_REGULARIZATION, gt=0.0)
    run_vqe_on_all_fragments: bool = False
    per_fragment_vqe_maxiter: int | None = Field(default=None, ge=1, le=500_000)
    bath_sidecar_json_path: str | None = None

    @field_validator("bath_sidecar_json_path")
    @classmethod
    def _strip_bath_sidecar(cls, v: str | None) -> str | None:
        return strip_optional_text(v)


class DmetEmbeddingSpec(ForbidExtraBase):
    fragment_labels: list[str] = Field(default_factory=list)
    hamiltonian_source: DmetHamiltonianSource = DmetHamiltonianSource.PARITY_STUB
    target_fragment_electrons: float | None = None
    uniform_multifragment_toy: bool = False
    multifragment_one_shot_shared_hamiltonian: bool = False
    fragment_solver: DmetFragmentSolverSpec = Field(default_factory=DmetFragmentSolverSpec)
    schmidt: SchmidtEmbeddingSpec = Field(default_factory=SchmidtEmbeddingSpec)

    @field_validator("fragment_labels", mode="before")
    @classmethod
    def _normalize_fragment_labels(cls, v: object) -> list[str]:
        if v is None:
            return []
        if not isinstance(v, (list, tuple)):
            raise ValueError(
                "embedding.dmet.fragment_labels must be a list of strings "
                f"(got {type(v).__name__})."
            )
        return [str(label).strip() for label in v if str(label).strip()]


class ProjectionEmbeddingSpec(ForbidExtraBase):
    low_level: str = "HF"
    high_level: str = "CAS"
    threshold: float = Field(default=PROJECTION_EMBEDDING_THRESHOLD, gt=0)
    quantum_hamiltonian: ProjectionQuantumHamiltonian = (
        ProjectionQuantumHamiltonian.GLOBAL_ACTIVE_SPACE
    )
    fragment_atom_indices: list[int] = Field(default_factory=list)


class PluginEmbeddingSpec(ForbidExtraBase):
    name: str = ""
    json_path: str | None = None

    @field_validator("json_path")
    @classmethod
    def _strip_json_path(cls, v: str | None) -> str | None:
        return strip_optional_text(v)


class EmbeddingBase(ForbidExtraBase):
    embedding_input_representation: EmbeddingInputRepresentation = EmbeddingInputRepresentation.MO
    n_scf_cycles_embedding: int | None = None
    classical_reference_method: str | None = None
    oniom_layers_v1: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def _cross_field(self) -> EmbeddingBase:
        from ._embedding_validation import validate_embedding_cross_fields

        validate_embedding_cross_fields(self)
        return self


class EmbeddingNone(EmbeddingBase):
    mode: Literal[EmbeddingMode.NONE] = EmbeddingMode.NONE


class EmbeddingDmet(EmbeddingBase):
    mode: Literal[EmbeddingMode.DMET] = EmbeddingMode.DMET
    dmet: DmetEmbeddingSpec = Field(default_factory=DmetEmbeddingSpec)


class EmbeddingProjection(EmbeddingBase):
    mode: Literal[EmbeddingMode.PROJECTION] = EmbeddingMode.PROJECTION
    projection: ProjectionEmbeddingSpec = Field(default_factory=ProjectionEmbeddingSpec)


class EmbeddingPlugin(EmbeddingBase):
    mode: Literal[EmbeddingMode.PLUGIN] = EmbeddingMode.PLUGIN
    plugin: PluginEmbeddingSpec = Field(default_factory=PluginEmbeddingSpec)

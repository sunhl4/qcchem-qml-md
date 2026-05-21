"""Quantum-stage algorithm configuration (nested YAML blocks).

Field reference: ``docs/说明_quantum配置.md``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ._quantum_validation import (
    validate_algorithm_registered_or_factory,
    validate_pauli_shot_mode_mutually_exclusive,
    validate_uccsd_trotter_steps,
    validate_vqd_max_overlap_warn_nonneg,
    validate_vqd_penalty_weights_len,
)
from ._validation import strip_optional_text, strip_required_text
from .quantum_enums import OperatorPoolId
from .quantum_graph import ComputableGraphEdgeDecl, ComputableGraphEdgeRemove
from .quantum_specs import (
    QuantumAdaptSpec,
    QuantumDemosSpec,
    QuantumExcitedSpec,
    QuantumGraphSpec,
    QuantumIqebSpec,
    QuantumPauliSpec,
    QuantumTensornetSpec,
    QuantumVariationalSpec,
    QuantumVqeSpec,
)

_FORBID = ConfigDict(extra="forbid")


class QuantumSpec(BaseModel):
    """Quantum stage after classical downfolding and qubit Hamiltonian build."""

    model_config = _FORBID

    algorithm: str = Field(
        default="vqe",
        description="Built-in variational id or label when algorithm_factory is set.",
    )
    algorithm_factory: str | None = Field(
        default=None,
        description="Import path module:callable for custom variational runner.",
    )
    variational: QuantumVariationalSpec = Field(default_factory=QuantumVariationalSpec)
    vqe: QuantumVqeSpec = Field(default_factory=QuantumVqeSpec)
    adapt: QuantumAdaptSpec = Field(default_factory=QuantumAdaptSpec)
    iqeb: QuantumIqebSpec = Field(default_factory=QuantumIqebSpec)
    pauli: QuantumPauliSpec = Field(default_factory=QuantumPauliSpec)
    excited: QuantumExcitedSpec = Field(default_factory=QuantumExcitedSpec)
    demos: QuantumDemosSpec = Field(default_factory=QuantumDemosSpec)
    tensornet: QuantumTensornetSpec = Field(default_factory=QuantumTensornetSpec)
    graph: QuantumGraphSpec = Field(default_factory=QuantumGraphSpec)

    def qpe_demo_track_requested(self) -> bool:
        return self.demos.qpe.track_requested()

    def qpe_three_pack_requested(self) -> bool:
        return self.demos.qpe.three_pack_requested()

    def vqs_track_requested(self) -> bool:
        return self.demos.vqs.track_requested()

    @field_validator("algorithm")
    @classmethod
    def _strip_algorithm(cls, v: str) -> str:
        return strip_required_text(v, field_name="quantum.algorithm")

    @field_validator("algorithm_factory")
    @classmethod
    def _normalize_algorithm_factory(cls, v: str | None) -> str | None:
        return strip_optional_text(v)

    @model_validator(mode="after")
    def _algorithm_registered_or_factory(self) -> QuantumSpec:
        validate_algorithm_registered_or_factory(self)
        return self

    @model_validator(mode="after")
    def _pauli_shot_mode_mutually_exclusive(self) -> QuantumSpec:
        validate_pauli_shot_mode_mutually_exclusive(self)
        return self

    @model_validator(mode="after")
    def _uccsd_trotter_steps_valid(self) -> QuantumSpec:
        validate_uccsd_trotter_steps(self)
        return self

    @model_validator(mode="after")
    def _vqd_penalty_weights_len(self) -> QuantumSpec:
        validate_vqd_penalty_weights_len(self)
        return self

    @field_validator("excited", mode="before")
    @classmethod
    def _normalize_excited_vqd_warn(cls, v: object) -> object:
        if not isinstance(v, dict):
            return v
        vqd = v.get("vqd")
        if isinstance(vqd, dict) and "max_overlap_warn" in vqd:
            vqd["max_overlap_warn"] = validate_vqd_max_overlap_warn_nonneg(
                vqd.get("max_overlap_warn")
            )
        return v


__all__ = [
    "ComputableGraphEdgeDecl",
    "ComputableGraphEdgeRemove",
    "OperatorPoolId",
    "QuantumSpec",
]

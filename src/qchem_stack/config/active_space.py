"""Active-space sizing and fermion-to-qubit mapping (nested YAML).

Field reference: ``docs/说明_active_space配置.md``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ._active_space_validation import (
    normalize_active_space_entry,
    validate_frozen_orbitals,
    validate_jw_optimizer_flags,
)
from .active_space_mapping_specs import ActiveSpaceMappingSpec
from .active_space_specs import ActiveSpaceCasSpec, ActiveSpaceJwSpec, ActiveSpaceManualSpec

_FORBID = ConfigDict(extra="forbid")


class ActiveSpaceSpec(BaseModel):
    """Active-space sizing, strategy, and fermion-to-qubit mapping."""

    model_config = _FORBID

    strategy: Literal["manual", "cas", "avas_stub", "avas"] = Field(
        default="cas",
        description="Active-space selection strategy.",
    )
    mapping: ActiveSpaceMappingSpec = Field(default_factory=ActiveSpaceMappingSpec)
    cas: ActiveSpaceCasSpec = Field(default_factory=ActiveSpaceCasSpec)
    manual: ActiveSpaceManualSpec = Field(default_factory=ActiveSpaceManualSpec)
    jw: ActiveSpaceJwSpec = Field(default_factory=ActiveSpaceJwSpec)

    @field_validator("manual")
    @classmethod
    def _validate_frozen_orbitals_block(cls, v: ActiveSpaceManualSpec) -> ActiveSpaceManualSpec:
        if v.frozen_orbitals:
            validate_frozen_orbitals(v.frozen_orbitals)
        return v

    @model_validator(mode="after")
    def _normalize_active_space_entry(self) -> ActiveSpaceSpec:
        normalize_active_space_entry(self)
        return self

    @model_validator(mode="after")
    def _jw_optimizer_flags_consistent(self) -> ActiveSpaceSpec:
        validate_jw_optimizer_flags(self)
        return self

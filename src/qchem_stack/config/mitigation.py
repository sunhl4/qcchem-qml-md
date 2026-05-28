"""Mitigation orchestration options for parity and runtime stubs."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from ._base import ForbidExtraBase
from ._mitigation_validation import validate_mitigation_cross_fields
from .mitigation_specs import MitigationPmsvSpec, MitigationStubsSpec, MitigationZneSpec


class MitigationSpec(ForbidExtraBase):
    """Classify mitigation by orchestration topology (sync graph vs async batch)."""

    execution_class: Literal["unspecified", "sync_graph", "async_batch", "shot_postselect"] = Field(
        default="unspecified",
        description="Mitigation orchestration topology class.",
    )
    zne: MitigationZneSpec = Field(default_factory=MitigationZneSpec)
    pmsv: MitigationPmsvSpec = Field(default_factory=MitigationPmsvSpec)
    stubs: MitigationStubsSpec = Field(default_factory=MitigationStubsSpec)

    @model_validator(mode="after")
    def _mitigation_cross_fields(self) -> MitigationSpec:
        validate_mitigation_cross_fields(self)
        return self

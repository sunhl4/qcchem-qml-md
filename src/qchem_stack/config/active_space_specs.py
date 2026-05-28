"""Nested active_space sub-schemas."""

from __future__ import annotations

from pydantic import Field

from ._base import ForbidExtraBase


class ActiveSpaceCasSpec(ForbidExtraBase):
    n_orbitals: int | None = Field(default=None, ge=1, description="Active spatial orbital count.")
    n_electrons: int | None = Field(default=None, ge=1, description="Active electron count.")


class ActiveSpaceManualSpec(ForbidExtraBase):
    n_orbitals: int | None = Field(default=None, ge=1, description="Active orbital count.")
    n_electrons: int | None = Field(default=None, ge=1, description="Active electron count.")
    frozen_orbitals: list[int] = Field(
        default_factory=list,
        description="Frozen core indices (manual strategy only).",
    )


class ActiveSpaceJwSpec(ForbidExtraBase):
    prefer_restricted_spatial: bool = Field(
        default=False,
        description="JW path from spatial MO integrals (no dense spin ERI).",
    )
    coeff_atol: float | None = Field(
        default=None,
        description="Optional JW coefficient cutoff (positive when set).",
    )

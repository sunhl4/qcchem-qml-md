"""Nested mitigation sub-schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ._base import ForbidExtraBase


class MitigationZneSpec(ForbidExtraBase):
    enabled: bool = Field(default=False, description="Enable ZNE stub path.")
    mode: Literal["scalar_stub", "circuit_scale_fold"] = Field(
        default="scalar_stub", description="ZNE mode."
    )
    scales: list[float] = Field(
        default_factory=lambda: [1.0, 1.5, 2.0],
        description="Noise amplification scale factors.",
    )


class MitigationPmsvSpec(ForbidExtraBase):
    enabled: bool = Field(default=False, description="Enable PMSV post-selection stub.")
    stabilizers: list[str] = Field(default_factory=list, description="PMSV stabilizer labels.")
    retention_rate: float = Field(
        default=1.0, gt=0.0, le=1.0, description="Post-selection retention rate."
    )
    report_extension: str = Field(default="default", description="PMSV report hook name.")
    extra: dict[str, Any] = Field(default_factory=dict, description="Opaque PMSV metadata.")


class MitigationStubsSpec(ForbidExtraBase):
    spam_calibration: bool = Field(default=False, description="Readout correction stub node.")
    pec_literature: bool = Field(
        default=False, description="PEC literature stub in parity snapshot."
    )
    classical_shadows: bool = Field(default=False, description="Classical shadows stub node.")
    classical_shadows_budget_pairs: int = Field(
        default=256,
        ge=1,
        le=10_000_000,
        description="Shadows budget hint for Methods export.",
    )

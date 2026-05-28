"""Compiler pass configuration shared by backends and export surfaces."""

from __future__ import annotations

from pydantic import Field, field_validator

from ._base import ForbidExtraBase
from ._validation import strip_required_text


class CompilerSpec(ForbidExtraBase):
    """Pass bundles analogous to vendor ``preoptimize_passes`` / ``compiler_passes`` knobs."""

    optimization_level: int = Field(
        default=1,
        ge=0,
        le=3,
        description="Logical optimization tier (0=minimal, 3=aggressive).",
    )
    native_twoq: str = Field(
        default="CX",
        min_length=1,
        description="Native two-qubit gate name for backend lowering (e.g. CX, CZ).",
    )
    preoptimize_passes: list[str] = Field(
        default_factory=list,
        description="Ansatz- or chemistry-adjacent logical passes (see :mod:`qchem_stack.backends.compile_passes`).",
    )
    compiler_passes: list[str] = Field(
        default_factory=list,
        description="Target-backend passes applied after ``preoptimize_passes``.",
    )

    @field_validator("native_twoq")
    @classmethod
    def _normalize_native_twoq(cls, value: str) -> str:
        return strip_required_text(value, field_name="compiler.native_twoq").upper()

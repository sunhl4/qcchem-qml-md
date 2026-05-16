"""Compiler pass configuration shared by backends and export surfaces."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from ._validation import strip_required_text


class CompilerSpec(BaseModel):
    """Pass bundles analogous to vendor ``preoptimize_passes`` / ``compiler_passes`` knobs."""

    optimization_level: int = Field(default=1, ge=0, le=3)
    native_twoq: str = Field(default="CX", min_length=1)
    preoptimize_passes: list[str] = Field(default_factory=list)
    """Ansatz- or chemistry-adjacent logical passes (see :mod:`qchem_stack.backends.compile_passes`)."""
    compiler_passes: list[str] = Field(default_factory=list)
    """Target-backend passes applied after ``preoptimize_passes``."""

    @field_validator("native_twoq")
    @classmethod
    def _normalize_native_twoq(cls, value: str) -> str:
        return strip_required_text(value, field_name="compiler.native_twoq").upper()

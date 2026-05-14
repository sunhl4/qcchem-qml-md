"""Backend execution configuration for protocol/runtime adapters."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from ._validation import strip_optional_text


class BackendSpecConfig(BaseModel):
    """Execution backend selection and shot/noise controls."""

    name: str = Field(default="statevector_sim", min_length=1)
    provider: Literal["statevector", "qiskit", "ionstack"] = "statevector"
    shots_per_circuit: int = Field(default=2048, ge=1)
    target_energy_stderr: float | None = Field(default=None, gt=0.0)
    qiskit_mode: Literal["statevector", "estimator"] = "statevector"
    ionstack_endpoint: str | None = Field(default=None, min_length=1)
    meta: dict[str, Any] = Field(default_factory=dict)

    @field_validator("ionstack_endpoint")
    @classmethod
    def _normalize_ionstack_endpoint(cls, value: str | None) -> str | None:
        return strip_optional_text(value)

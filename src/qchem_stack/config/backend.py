"""Backend execution configuration for protocol/runtime adapters."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, field_validator

from ._base import ForbidExtraBase
from ._validation import strip_optional_text


class BackendSpecConfig(ForbidExtraBase):
    """Execution backend selection and shot/noise controls."""

    name: str = Field(default="statevector_sim", min_length=1)
    provider: Literal[
        "statevector",
        "qiskit",
        "ionstack",
        "uqc",
        "qulacs",
        "cirq",
        "braket",
    ] = "statevector"
    shots_per_circuit: int = Field(default=2048, ge=1)
    target_energy_stderr: float | None = Field(default=None, gt=0.0)
    qiskit_mode: Literal["statevector", "estimator"] = "statevector"
    ionstack_endpoint: str | None = Field(default=None, min_length=1)
    # UQC cloud platform configuration
    uqc_token: str | None = Field(
        default=None,
        description="UQC API token (can also be set via UQC_API_TOKEN env var)",
    )
    uqc_backend_name: str | None = Field(
        default=None,
        description="UQC backend name (e.g., 'ion_trap_1')",
    )
    uqc_mode: Literal["real", "mock"] = Field(
        default="real",
        description="UQC execution mode: real (submit to cloud) or mock (use statevector simulator)",
    )
    uqc_transpile_opt_level: int = Field(
        default=2,
        ge=0,
        le=3,
        description="Qiskit transpiler optimization level for UQC native gate conversion",
    )
    meta: dict[str, Any] = Field(default_factory=dict)

    @field_validator("ionstack_endpoint")
    @classmethod
    def _normalize_ionstack_endpoint(cls, value: str | None) -> str | None:
        return strip_optional_text(value)

    @field_validator("uqc_token", "uqc_backend_name")
    @classmethod
    def _strip_uqc_optional_text(cls, value: str | None) -> str | None:
        return strip_optional_text(value)

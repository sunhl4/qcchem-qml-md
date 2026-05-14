"""Nexus-shaped local ledger and optional cloud adapter settings."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from ._validation import strip_required_text


class NexusAnalogSpec(BaseModel):
    """Local project + HQC **unit** ledger (no Nexus API, no real billing)."""

    enabled: bool = False
    project_label: str = Field(default="default", min_length=1)
    unit_per_circuit: float = Field(default=1.0, ge=0.0)
    unit_per_shot: float = Field(default=1e-4, ge=0.0)
    unit_per_depth: float = Field(default=1e-3, ge=0.0)

    @field_validator("project_label")
    @classmethod
    def _strip_project_label(cls, value: str) -> str:
        return strip_required_text(value, field_name="nexus_analog.project_label")


class NexusCloudSpec(BaseModel):
    """
    Optional real **Nexus/Quantinuum cloud** job adapter (opt-in, no secrets in YAML).

    Use ``NEXUS_API_KEY`` (or :attr:`api_key_env`) in the process environment; the open stack
    only ships a typed client + health/submit shims, not a vendor contract.
    """

    mode: Literal["off", "http", "mock"] = "off"
    base_url: str = ""
    """HTTPS API root (e.g. ``https://nexus.../v1``) — use only in ``http`` mode."""
    api_key_env: str = Field(default="NEXUS_API_KEY", min_length=1)
    project_slug: str = ""
    timeout_s: float = Field(default=30.0, gt=0.0)

    @field_validator("api_key_env")
    @classmethod
    def _strip_api_key_env(cls, value: str) -> str:
        return strip_required_text(value, field_name="nexus_cloud.api_key_env")

    @field_validator("project_slug", "base_url")
    @classmethod
    def _strip_cloud_optional_text(cls, value: str) -> str:
        return value.strip()

"""Nexus-shaped local ledger and optional cloud adapter settings."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator

from qchem_stack.quantum.algorithms.tolerances import UNIT_PER_DEPTH, UNIT_PER_SHOT

from ._base import ForbidExtraBase
from ._validation import strip_required_text


class NexusAnalogSpec(ForbidExtraBase):
    enabled: bool = False
    project_label: str = Field(default="default", min_length=1)
    unit_per_circuit: float = Field(default=1.0, ge=0.0)
    unit_per_shot: float = Field(default=UNIT_PER_SHOT, ge=0.0)
    unit_per_depth: float = Field(default=UNIT_PER_DEPTH, ge=0.0)

    @field_validator("project_label")
    @classmethod
    def _strip_project_label(cls, value: str) -> str:
        return strip_required_text(value, field_name="nexus_analog.project_label")


class NexusCloudSpec(ForbidExtraBase):
    mode: Literal["off", "http", "mock"] = Field(
        default="off",
        description="Cloud adapter mode: off (default), http (real HTTPS client), or mock.",
    )
    base_url: str = Field(
        default="",
        description="HTTPS API root (e.g. ``https://nexus.../v1``) — use only in ``http`` mode.",
    )
    api_key_env: str = Field(default="NEXUS_API_KEY", min_length=1)
    project_slug: str = Field(
        default="", description="Optional Nexus project slug for cloud submit."
    )
    timeout_s: float = Field(default=30.0, gt=0.0)

    @field_validator("api_key_env")
    @classmethod
    def _strip_api_key_env(cls, value: str) -> str:
        return strip_required_text(value, field_name="nexus_cloud.api_key_env")

    @field_validator("project_slug", "base_url")
    @classmethod
    def _strip_cloud_optional_text(cls, value: str) -> str:
        return value.strip()

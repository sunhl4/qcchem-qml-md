"""Base class for configuration models with extra="forbid"."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ForbidExtraBase(BaseModel):
    """Base class that forbids extra fields in Pydantic models.

    All configuration specs should inherit from this class instead of
    directly setting `model_config = ConfigDict(extra="forbid")`.
    """

    model_config = ConfigDict(extra="forbid")

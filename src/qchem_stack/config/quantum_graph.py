"""Computable DAG edge declarations for workflow preview."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ComputableGraphEdgeDecl(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_ref: str = Field(description="Source computable name.")
    to_ref: str = Field(description="Target computable name.")
    kind: str = Field(default="declared_dataflow", description="Edge kind label for preview UX.")


class ComputableGraphEdgeRemove(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_ref: str = Field(description="Source computable name.")
    to_ref: str = Field(description="Target computable name.")

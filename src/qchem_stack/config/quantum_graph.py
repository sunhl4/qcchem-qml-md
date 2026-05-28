"""Computable DAG edge declarations for workflow preview."""

from __future__ import annotations

from pydantic import Field

from ._base import ForbidExtraBase


class ComputableGraphEdgeDecl(ForbidExtraBase):
    from_ref: str = Field(description="Source computable name.")
    to_ref: str = Field(description="Target computable name.")
    kind: str = Field(default="declared_dataflow", description="Edge kind label for preview UX.")


class ComputableGraphEdgeRemove(ForbidExtraBase):
    from_ref: str = Field(description="Source computable name.")
    to_ref: str = Field(description="Target computable name.")

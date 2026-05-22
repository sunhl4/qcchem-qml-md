"""Helpers for copying and extending classical ``driver_meta`` payloads."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping


def fork_driver_meta(meta: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return a shallow mutable copy suitable for downstream mutation."""
    return dict(meta or {})


def readonly_driver_meta(meta: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """Return a read-only view over ``driver_meta`` without copying nested values."""
    return MappingProxyType(dict(meta or {}))


def merge_driver_meta_updates(
    meta: Mapping[str, Any] | None,
    /,
    **updates: Any,
) -> dict[str, Any]:
    """Fork ``meta`` and apply scalar/top-level updates."""
    out = fork_driver_meta(meta)
    out.update(updates)
    return out

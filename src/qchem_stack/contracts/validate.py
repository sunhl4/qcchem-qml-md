"""Lightweight schema-id guards for JSON-ish dict payloads."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping


def assert_payload_schema(
    payload: Mapping[str, Any],
    schema_id: str,
    *,
    field: str = "schema",
) -> None:
    """Raise ``ValueError`` when ``payload[field]`` does not match ``schema_id``."""
    found = payload.get(field)
    if found != schema_id:
        raise ValueError(f"expected {field}={schema_id!r}, got {found!r}")


def schema_field(schema_id: str) -> dict[str, str]:
    """Return a single-key dict suitable for merging into API/repro payloads."""
    return {"schema": schema_id}

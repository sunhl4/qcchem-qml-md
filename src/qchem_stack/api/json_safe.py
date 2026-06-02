"""Strict JSON helpers for HTTP API responses (no ``default=str``)."""

from __future__ import annotations

import json
from typing import Any

from qchem_stack.repro.export import repro_dict_for_strict_json, repro_json_dumps


def api_payload_for_json(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a deep JSON-native dict suitable for stable ETag hashing."""
    return repro_dict_for_strict_json(payload)


def api_json_dumps(payload: dict[str, Any], *, sort_keys: bool = True) -> str:
    """Canonical UTF-8 JSON text for API bodies (RFC-compliant, no NaN)."""
    safe = api_payload_for_json(payload)
    return json.dumps(
        safe,
        sort_keys=sort_keys,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def api_json_dumps_from_repro_helper(payload: dict[str, Any]) -> str:
    """Alias using the same path as ``repro_json_dumps`` (sorted keys optional)."""
    return repro_json_dumps(payload, indent=None)

"""HTTP API contract version for stable /v1 routes (since package 1.0.0)."""

from __future__ import annotations

from typing import Any

API_CONTRACT_VERSION = "1.0"


def with_api_contract(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy with ``api_contract_version`` set (idempotent)."""
    out = dict(payload)
    out.setdefault("api_contract_version", API_CONTRACT_VERSION)
    return out

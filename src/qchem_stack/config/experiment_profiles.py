"""Named experiment profile overlays (distinct from backend execution profiles)."""

from __future__ import annotations

from typing import Any

EXPERIMENT_PROFILES: dict[str, dict[str, Any]] = {
    "minimal": {
        "schema_version": "2",
        "scf": {
            "driver": "precomputed",
            "method": "RHF",
            "precomputed": {"bundle_path": "configs/precomputed_classical_reference_h2.json"},
        },
        "quantum": {"pauli": {"use_protocol": False}},
        "embedding": {"mode": "none"},
    },
    "research": {
        "parity_integrations": {
            "resource_estimation_preview": True,
            "include_computables_rich_in_repro": True,
        },
    },
    "production": {
        "parity_integrations": {"resource_estimation_preview": True},
        "quantum": {"pauli": {"use_protocol": True}},
    },
}


def apply_experiment_profile(cfg_dict: dict[str, Any], profile_id: str) -> dict[str, Any]:
    """Deep-merge a named profile overlay onto a YAML dict (profile keys win on conflict)."""
    if profile_id not in EXPERIMENT_PROFILES:
        raise KeyError(f"unknown experiment profile: {profile_id!r}")
    return _deep_merge(dict(cfg_dict), EXPERIMENT_PROFILES[profile_id])


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out

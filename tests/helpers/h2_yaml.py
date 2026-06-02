"""Shared H2 sto-3g YAML dict fixtures for pipeline tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

# Canonical FCI reference energy (sto-3g H2, ~0.74 bohr bond).
H2_STO3G_FCI_ENERGY = -1.1372759436170443


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, val in override.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def h2_yaml_dict(**overrides: Any) -> dict[str, Any]:
    """Minimal H2 experiment dict; nested overrides merge recursively."""
    base: dict[str, Any] = {
        "schema_version": "2",
        "experiment_id": "combo_test",
        "random_seed": 1,
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
            "coordinate_unit": "bohr",
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "active_space": {
            "strategy": "cas",
            "cas": {"n_orbitals": 2, "n_electrons": 2},
        },
        "scf": {"driver": "pyscf", "method": "RHF"},
        "embedding": {"mode": "none"},
        "quantum": {
            "algorithm": "vqe",
            "vqe": {"depth": 1, "maxiter": 5},
            "pauli": {"use_protocol": False},
        },
    }
    if not overrides:
        return base
    return _deep_merge(base, overrides)


def h2_pipeline_dict(**overrides: Any) -> dict[str, Any]:
    """H2 dict with typical pipeline defaults (backend + pauli protocol on)."""
    base = h2_yaml_dict(
        backend={"provider": "statevector", "shots_per_circuit": 512},
        quantum={
            "algorithm": "vqe",
            "vqe": {"depth": 1, "maxiter": 120},
            "pauli": {"use_protocol": True},
        },
    )
    if not overrides:
        return base
    return _deep_merge(base, overrides)


def write_experiment_yaml(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def write_h2_pipeline_yaml(path: Path, **overrides: Any) -> Path:
    return write_experiment_yaml(path, h2_pipeline_dict(**overrides))


# Aliases for callers that prefer explicit naming in the plan / docs.
h2_yaml_with = h2_yaml_dict


def write_h2_config(path: Path, **overrides: Any) -> Path:
    """Write a minimal H2 experiment YAML (not the full pipeline defaults)."""
    return write_experiment_yaml(path, h2_yaml_dict(**overrides))

"""Compatibility shim for UQC environment helpers."""

from __future__ import annotations

import os
from pathlib import Path

# Repo root: src/qchem_stack/backends -> parents[3]
_REPO_ROOT = Path(__file__).resolve().parents[3]


def load_repo_dotenv() -> None:
    """Set env vars from ``<repo>/.env`` if not already defined."""
    env_path = _REPO_ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = val


__all__ = ["_REPO_ROOT", "load_repo_dotenv"]

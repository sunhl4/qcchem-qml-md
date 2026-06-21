"""Resolve packaged and development config directory locations."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def repo_configs_dir() -> Path | None:
    """Return ``<repo>/configs`` when running from an editable / source checkout."""
    candidate = Path(__file__).resolve().parents[3] / "configs"
    return candidate.resolve() if candidate.is_dir() else None


def installed_share_configs_dir() -> Path | None:
    """Return wheel-installed configs under ``share/qchem-stack/configs``."""
    candidate = Path(sys.prefix) / "share" / "qchem-stack" / "configs"
    return candidate.resolve() if candidate.is_dir() else None


def default_configs_dir() -> Path:
    """Best-effort configs root for CLI and scenario resolution.

    Priority:
    1. ``QCHEM_STACK_CONFIGS_DIR`` environment variable
    2. ``./configs`` relative to the current working directory
    3. Repository ``configs/`` (editable install / dev tree)
    4. Wheel ``share/qchem-stack/configs`` (``pip install``)
    """
    explicit = os.environ.get("QCHEM_STACK_CONFIGS_DIR")
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.is_dir():
            return path

    cwd_configs = (Path.cwd() / "configs").resolve()
    if cwd_configs.is_dir():
        return cwd_configs

    repo_configs = repo_configs_dir()
    if repo_configs is not None:
        return repo_configs

    share_configs = installed_share_configs_dir()
    if share_configs is not None:
        return share_configs

    return cwd_configs

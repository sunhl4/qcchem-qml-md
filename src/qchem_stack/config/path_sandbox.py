"""Filesystem path allowlists for config-relative assets (geometry, precomputed bundles)."""

from __future__ import annotations

import os
from pathlib import Path

from qchem_stack.config.config_paths import installed_share_configs_dir, repo_configs_dir


class ConfigBaseDirError(Exception):
    """Raised when a config base directory is outside the allowlist."""


def allowed_config_base_dirs() -> list[Path]:
    """Directories permitted for ``config_base_dir`` / geometry file resolution."""
    dirs: list[Path] = []
    explicit = os.environ.get("QCHEM_STACK_CONFIG_BASE_DIR")
    if explicit:
        dirs.append(Path(explicit).expanduser().resolve())
    repo_configs = repo_configs_dir()
    if repo_configs is not None:
        dirs.append(repo_configs)
    share_configs = installed_share_configs_dir()
    if share_configs is not None:
        dirs.append(share_configs)
    if not dirs:
        dirs.append(Path.cwd().resolve())
    return dirs


def validate_config_base_dir(raw: str) -> Path:
    """Resolve and validate a user-supplied config base directory."""
    if not raw or not str(raw).strip():
        raise ConfigBaseDirError("config_base_dir must be a non-empty string when provided")
    resolved = Path(raw).expanduser().resolve()
    if not resolved.is_dir():
        raise ConfigBaseDirError(f"config_base_dir is not a directory: {resolved}")
    allowed = allowed_config_base_dirs()
    if not any(str(resolved).startswith(str(base)) for base in allowed):
        raise ConfigBaseDirError(
            f"config_base_dir outside allowed directories: {[str(d) for d in allowed]}"
        )
    return resolved

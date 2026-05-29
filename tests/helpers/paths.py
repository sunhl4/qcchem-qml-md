"""Path helpers for tests (repo root independent of tests/ nesting depth).

Use these instead of ``Path(__file__).resolve().parents[N]`` so tests stay valid
when moved between ``tests/``, ``tests/quantum/``, ``tests/config/``, etc.
"""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    raise RuntimeError("repo root not found (no pyproject.toml in parents)")


def configs_path(yaml_name: str) -> Path:
    return repo_root() / "configs" / yaml_name


def configs_dir() -> Path:
    return repo_root() / "configs"


def docs_path(rel: str) -> Path:
    return repo_root() / "docs" / rel


def fixtures_path(rel: str) -> Path:
    return repo_root() / "tests" / "fixtures" / rel


def scripts_path(rel: str) -> Path:
    return repo_root() / "scripts" / rel

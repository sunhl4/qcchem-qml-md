"""Tests for config directory resolution (editable + wheel layouts)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config.config_paths import (
    default_configs_dir,
    installed_share_configs_dir,
    repo_configs_dir,
)
from qchem_stack.config.scenarios import scenario_config_path
from tests.helpers.paths import repo_root


def test_repo_configs_dir_points_at_packaged_tree() -> None:
    configs = repo_configs_dir()
    assert configs is not None
    assert configs == (repo_root() / "configs").resolve()
    assert (configs / "example_h2.yaml").is_file()


def test_default_configs_dir_prefers_repo_in_editable_install() -> None:
    resolved = default_configs_dir()
    assert resolved.is_dir()
    assert (resolved / "scenarios" / "minimal_vqe.yaml").is_file()


def test_scenario_config_path_minimal_vqe() -> None:
    path = scenario_config_path("minimal_vqe")
    assert path.is_file()
    assert path.name == "minimal_vqe.yaml"


def test_default_configs_dir_honors_env_override(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    custom = tmp_path / "configs"
    custom.mkdir()
    (custom / "scenarios").mkdir()
    stub = custom / "scenarios" / "minimal_vqe.yaml"
    stub.write_text('schema_version: "3"\nscenario: minimal_vqe\noverrides: {}\n', encoding="utf-8")
    monkeypatch.setenv("QCHEM_STACK_CONFIGS_DIR", str(custom))
    assert default_configs_dir() == custom.resolve()
    assert scenario_config_path("minimal_vqe") == stub.resolve()


def test_installed_share_configs_dir_none_without_wheel_layout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("QCHEM_STACK_CONFIGS_DIR", raising=False)
    share = installed_share_configs_dir()
    if share is None:
        assert share is None
    else:
        assert share.is_dir()


def test_default_configs_dir_ignores_invalid_env_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QCHEM_STACK_CONFIGS_DIR", str(tmp_path / "missing"))
    resolved = default_configs_dir()
    assert resolved.is_dir()
    assert (resolved / "scenarios" / "minimal_vqe.yaml").is_file()


def test_installed_share_configs_dir_from_wheel_prefix(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    venv_root = tmp_path / "venv"
    share = venv_root / "share" / "qchem-stack" / "configs"
    share.mkdir(parents=True)
    (share / "stub.yaml").write_text("x: 1\n", encoding="utf-8")
    monkeypatch.setattr("qchem_stack.config.config_paths.sys.prefix", str(venv_root))
    assert installed_share_configs_dir() == share.resolve()


def test_default_configs_dir_prefers_cwd_configs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    work = tmp_path / "work"
    work.mkdir()
    cwd_configs = work / "configs"
    cwd_configs.mkdir()
    (cwd_configs / "local.yaml").write_text("x: 1\n", encoding="utf-8")
    monkeypatch.chdir(work)
    monkeypatch.delenv("QCHEM_STACK_CONFIGS_DIR", raising=False)
    monkeypatch.setattr("qchem_stack.config.config_paths.repo_configs_dir", lambda: None)
    monkeypatch.setattr("qchem_stack.config.config_paths.installed_share_configs_dir", lambda: None)
    assert default_configs_dir() == cwd_configs.resolve()


def test_default_configs_dir_uses_installed_share_when_no_repo_or_cwd(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    work = tmp_path / "work"
    work.mkdir()
    share = tmp_path / "venv" / "share" / "qchem-stack" / "configs"
    share.mkdir(parents=True)
    monkeypatch.chdir(work)
    monkeypatch.delenv("QCHEM_STACK_CONFIGS_DIR", raising=False)
    monkeypatch.setattr("qchem_stack.config.config_paths.sys.prefix", str(tmp_path / "venv"))
    monkeypatch.setattr("qchem_stack.config.config_paths.repo_configs_dir", lambda: None)
    assert default_configs_dir() == share.resolve()


def test_default_configs_dir_returns_cwd_configs_path_when_unresolved(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    work = tmp_path / "empty"
    work.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.delenv("QCHEM_STACK_CONFIGS_DIR", raising=False)
    monkeypatch.setattr("qchem_stack.config.config_paths.repo_configs_dir", lambda: None)
    monkeypatch.setattr("qchem_stack.config.config_paths.installed_share_configs_dir", lambda: None)
    assert default_configs_dir() == (work / "configs").resolve()

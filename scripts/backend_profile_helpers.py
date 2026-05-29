#!/usr/bin/env python3
"""Shared helpers: load experiment YAML and apply a named backend profile."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qchem_stack.backends.profiles import BackendProfile
    from qchem_stack.config import ExperimentConfig


def load_experiment_with_backend_profile(
    experiment_yaml: Path,
    profile_id: str,
) -> tuple[ExperimentConfig, BackendProfile, Path]:
    """Load config and apply ``profile_id``; write resolved YAML beside caller output if needed."""
    from qchem_stack.backends.profiles import apply_backend_profile
    from qchem_stack.config import load_experiment_config

    cfg = load_experiment_config(experiment_yaml)
    prof = apply_backend_profile(cfg, profile_id)
    return cfg, prof, experiment_yaml


def write_resolved_experiment_yaml(
    cfg: ExperimentConfig,
    output_dir: Path,
    *,
    profile_id: str,
) -> Path:
    from qchem_stack.config import dump_experiment_config

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"experiment_resolved_{profile_id}.yaml"
    path.write_text(dump_experiment_config(cfg), encoding="utf-8")
    return path

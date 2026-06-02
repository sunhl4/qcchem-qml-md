"""Experiment profile overlays."""

from __future__ import annotations

from qchem_stack.config import ExperimentConfig
from qchem_stack.config.experiment_profiles import apply_experiment_profile
from tests.helpers.h2_yaml import h2_yaml_dict


def test_apply_research_profile_enables_preview() -> None:
    merged = apply_experiment_profile(h2_yaml_dict(), "research")
    cfg = ExperimentConfig.model_validate(merged)
    assert cfg.parity_integrations.resource_estimation_preview is True
    assert cfg.parity_integrations.include_computables_rich_in_repro is True


def test_apply_minimal_profile_sets_precomputed() -> None:
    merged = apply_experiment_profile(h2_yaml_dict(), "minimal")
    assert merged["scf"]["driver"] == "precomputed"

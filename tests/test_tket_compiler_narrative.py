"""TKET / CompilerSpec narrative: gap row and bundle signature stay in sync with Technical doc §2–4."""

from __future__ import annotations

import copy

import yaml

from qchem_stack.config import (
    CompilerSpec,
    ExperimentConfig,
    compiler_bundle_signature_from_config,
)
from qchem_stack.internal_reports.competitor.inquanto_contract import inquanto_gap_categories


def _minimal_h2_yaml() -> str:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    return (root / "configs" / "example_h2.yaml").read_text(encoding="utf-8")


def test_compiler_pass_bundle_gap_mentions_compiler_spec_and_signature() -> None:
    gaps = inquanto_gap_categories()
    row = next(g for g in gaps if g.get("id") == "compiler_pass_bundle")
    text = (row.get("qchem_stack") or "") + (row.get("inquanto_surface") or "")
    assert "CompilerSpec" in text
    assert "compiler_bundle_signature" in text
    assert "tket_fullchain" in text


def test_compiler_bundle_signature_stable_for_defaults() -> None:
    cfg = ExperimentConfig.from_yaml_dict(yaml.safe_load(_minimal_h2_yaml()))
    sig0 = compiler_bundle_signature_from_config(cfg)
    assert len(sig0) == 16
    assert compiler_bundle_signature_from_config(cfg) == sig0


def test_compiler_bundle_signature_changes_with_optimization_level() -> None:
    cfg = ExperimentConfig.from_yaml_dict(yaml.safe_load(_minimal_h2_yaml()))
    sig0 = compiler_bundle_signature_from_config(cfg)
    alt = copy.deepcopy(cfg)
    alt.compiler = CompilerSpec.model_validate(
        {**cfg.compiler.model_dump(), "optimization_level": 3}
    )
    assert compiler_bundle_signature_from_config(alt) != sig0


def test_experiment_config_embeds_default_compiler_spec() -> None:
    cfg = ExperimentConfig.from_yaml_dict(
        {
            "experiment_id": "x",
            "molecule": {"symbols": ["H"], "coordinates_bohr": [[0.0, 0.0, 0.0]]},
            "active_space": {"n_active_orbitals": 1, "n_active_electrons": 1},
        }
    )
    assert cfg.compiler.optimization_level == 1
    assert cfg.compiler.native_twoq == "CX"

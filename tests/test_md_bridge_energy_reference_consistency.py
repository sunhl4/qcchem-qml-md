"""Tests for MD/ML energy reference semantic validation."""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.exceptions import ConfigurationError
from qchem_stack.md_bridge.energy_reference import (
    prepare_loop_config,
    validate_loop_energy_consistency,
    warn_hf_forces_non_scf_energy,
)
from qchem_stack.md_bridge.md_loop_config import (
    FrameValidationRecord,
    MdValidationLoopConfig,
    MdValidationRoundLog,
)
from qchem_stack.md_bridge.md_loop_summary import build_md_validation_summary


def test_validate_loop_rejects_mismatched_validation_and_label_reference() -> None:
    cfg = MdValidationLoopConfig(
        label_energy_reference="variational",
        validation_energy_reference="scf",
    )
    with pytest.raises(ConfigurationError, match="validation_energy_reference"):
        validate_loop_energy_consistency(cfg, strict=True)


def test_validate_loop_warn_mode_when_not_strict() -> None:
    cfg = MdValidationLoopConfig(
        label_energy_reference="variational",
        validation_energy_reference="scf",
    )
    issues = validate_loop_energy_consistency(cfg, strict=False)
    assert issues


def test_validate_loop_rejects_hf_theory_with_variational_reference() -> None:
    cfg = MdValidationLoopConfig(
        label_energy_reference="variational",
        validation_theory_level="hf_scf",
    )
    with pytest.raises(ConfigurationError, match="hf_scf"):
        validate_loop_energy_consistency(cfg, strict=True)


def test_validate_loop_cross_yaml_experiment_mismatch() -> None:
    loop_cfg = MdValidationLoopConfig(label_energy_reference="variational")
    exp_cfg = load_experiment_config("configs/example_h2.yaml")
    exp_cfg.md_ml_export.attach_single_frame_to_repro = True
    exp_cfg.md_ml_export.energy_reference = "scf"
    with pytest.raises(ConfigurationError, match="md_ml_export"):
        validate_loop_energy_consistency(loop_cfg, exp_cfg, strict=True)


def test_warn_hf_forces_non_scf_energy() -> None:
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warn_hf_forces_non_scf_energy(
            energy_reference="variational",
            include_hf_nuclear_gradient=True,
        )
    assert any("HF analytic forces" in str(w.message) for w in caught)


def test_frame_validation_record_dual_delta_fields() -> None:
    rec = FrameValidationRecord(
        frame_index=0,
        time_ps=float("nan"),
        energy_qml_hartree=-0.01,
        energy_qchem_hartree=-0.3,
        delta_hartree=-0.29,
        abs_delta_hartree=0.29,
        converged=False,
        theory_level="full_pipeline",
        energy_reference_used="variational",
        delta_hartree_raw=0.29,
        abs_delta_hartree_raw=0.29,
    )
    assert rec.abs_delta_hartree_raw == 0.29


def test_build_md_validation_summary_exports_dual_delta_metrics(tmp_path: Path) -> None:
    frame = FrameValidationRecord(
        frame_index=0,
        time_ps=0.0,
        energy_qml_hartree=-0.01,
        energy_qchem_hartree=-0.3,
        delta_hartree=-0.29,
        abs_delta_hartree=0.29,
        converged=False,
        theory_level="full_pipeline",
        energy_reference_used="variational",
        delta_hartree_raw=0.31,
        abs_delta_hartree_raw=0.31,
    )
    log = MdValidationRoundLog(
        round_index=0,
        n_train_before=0,
        n_train_after=1,
        n_md_frames_sampled=1,
        max_abs_delta_hartree=0.29,
        mean_abs_delta_hartree=0.29,
        converged=False,
        frames=[frame],
    )
    cfg = MdValidationLoopConfig(
        label_energy_reference="variational",
        validation_energy_reference="variational",
        energy_tolerance_hartree=0.5,
    )
    summary = build_md_validation_summary(
        experiment_yaml=tmp_path / "exp.yaml",
        output_dir=tmp_path / "out",
        config=cfg,
        n_total_frames=1,
        round_logs=[log],
        converged=False,
        species_list=["H", "H"],
    )
    assert summary["max_abs_delta_hartree"] == pytest.approx(0.29)
    assert summary["max_abs_delta_hartree_raw"] == pytest.approx(0.31)
    assert summary["validation_energy_reference"] == "variational"


def test_prepare_loop_config_emits_screening_deprecation_warning() -> None:
    cfg = MdValidationLoopConfig(label_screening_theory_level="full_pipeline")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        prepare_loop_config(cfg)
    assert any("label_screening_theory_level" in str(w.message) for w in caught)

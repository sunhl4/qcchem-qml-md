"""Three-round MD validation loop with mock qchem labeler (no PySCF pipeline)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("jax_md")


def _mock_label_base(experiment_yaml, **kwargs):
    from qchem_stack.md_bridge.active_learning import mock_labeling_result

    del experiment_yaml, kwargs
    # classical_h2 Morse fit needs >=2 diatomic frames on cold-start train.
    return mock_labeling_result(
        [1, 1],
        [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.5]]],
    )


def _mock_qmef_frame(handle, positions_bohr, atomic_numbers, **kwargs):
    from qchem_stack.md_bridge import QMFrame

    del handle, kwargs
    pos = positions_bohr.tolist() if hasattr(positions_bohr, "tolist") else positions_bohr
    return QMFrame(
        atomic_numbers=list(atomic_numbers),
        positions_bohr=pos,
        energy_hartree=-0.5,
        forces_hartree_bohr=[],
        method_tag="mock",
    ).model_dump(mode="json")


def _mock_predict_energy(handle, positions_bohr, atomic_numbers, **kwargs):
    import numpy as np

    del handle, kwargs
    n = len(atomic_numbers)
    return -0.5, np.zeros((n, 3), dtype=float)


def _mock_jaxmd_trajectory(handle, initial_positions_bohr, atomic_numbers, **kwargs):
    import numpy as np

    from qchem_stack.md_bridge.qmlff_md import JaxMdTrajectory

    del handle, kwargs
    base = np.asarray(initial_positions_bohr, dtype=float)
    stretched = base.copy()
    stretched[1, 2] += 0.05
    return JaxMdTrajectory(
        positions_bohr=[base, stretched],
        energies_hartree=[-1.0, -0.99],
        temperatures_K=[300.0, 300.0],
        times_ps=[0.0, 0.001],
        atomic_numbers=list(atomic_numbers),
        meta={"mock": True},
    )


def _mock_label_geometries(experiment_yaml, extra_coordinates_bohr, **kwargs):
    from qchem_stack.md_bridge.active_learning import mock_labeling_result

    del experiment_yaml, kwargs
    return mock_labeling_result(
        [1, 1],
        [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        extra_coordinates_bohr,
    )


def test_md_validation_loop_three_rounds_mock_labeler(tmp_path: Path) -> None:
    from qchem_stack.md_bridge import MdValidationLoopConfig, run_md_validation_loop

    exp_yaml = configs_path("example_h2.yaml")
    loop_cfg = MdValidationLoopConfig(
        max_rounds=3,
        force_field_backend="classical_h2",
        energy_tolerance_hartree=0.001,
        n_candidate_frames=1,
        add_top_k_per_round=1,
        validation_skip_initial_md_frame=True,
        label_screening_theory_level="hf_scf",
        label_top_theory_level="hf_scf",
        label_energy_reference="scf",
        validation_energy_reference="scf",
        md_n_steps=6,
        md_save_stride=3,
        n_epochs_per_round=1,
        write_per_round_extxyz=False,
    )
    out_dir = tmp_path / "md_multi_round_mock"

    with (
        patch(
            "qchem_stack.md_bridge.md_validation_loop.label_base_geometry_only",
            side_effect=_mock_label_base,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.label_geometries_with_pipeline",
            side_effect=_mock_label_geometries,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.run_jaxmd_trajectory",
            side_effect=_mock_jaxmd_trajectory,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_frame_scoring.predict_energy_forces_hartree",
            side_effect=_mock_predict_energy,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_frame_scoring.qmlff_handle_to_qmef_frame",
            side_effect=_mock_qmef_frame,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.compute_training_energy_shift_hartree",
            return_value=0.0,
        ),
    ):
        summary = run_md_validation_loop(
            exp_yaml,
            config=loop_cfg,
            output_dir=out_dir,
        )

    assert len(summary["rounds"]) == 3
    for r in summary["rounds"]:
        assert r.get("failures") == []
        assert int(r.get("n_md_frames_sampled") or 0) >= 1
    assert summary["n_total_frames"] >= 3
    assert (out_dir / "md_validation_summary.json").is_file()


@pytest.mark.l1_md_ml
def test_md_validation_loop_five_rounds_mock_labeler(tmp_path: Path) -> None:
    from qchem_stack.md_bridge import MdValidationLoopConfig, run_md_validation_loop

    exp_yaml = configs_path("example_h2.yaml")
    loop_cfg = MdValidationLoopConfig(
        max_rounds=5,
        force_field_backend="classical_h2",
        energy_tolerance_hartree=0.001,
        n_candidate_frames=1,
        add_top_k_per_round=1,
        validation_skip_initial_md_frame=True,
        label_screening_theory_level="hf_scf",
        label_top_theory_level="hf_scf",
        label_energy_reference="scf",
        validation_energy_reference="scf",
        md_n_steps=6,
        md_save_stride=3,
        n_epochs_per_round=1,
        write_per_round_extxyz=False,
    )
    out_dir = tmp_path / "md_five_round_mock"

    with (
        patch(
            "qchem_stack.md_bridge.md_validation_loop.label_base_geometry_only",
            side_effect=_mock_label_base,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.label_geometries_with_pipeline",
            side_effect=_mock_label_geometries,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.run_jaxmd_trajectory",
            side_effect=_mock_jaxmd_trajectory,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_frame_scoring.predict_energy_forces_hartree",
            side_effect=_mock_predict_energy,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_frame_scoring.qmlff_handle_to_qmef_frame",
            side_effect=_mock_qmef_frame,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.compute_training_energy_shift_hartree",
            return_value=0.0,
        ),
    ):
        summary = run_md_validation_loop(
            exp_yaml,
            config=loop_cfg,
            output_dir=out_dir,
        )

    assert len(summary["rounds"]) == 5
    assert "science_kpi_met" in summary
    assert "max_abs_delta_hartree" in summary
    assert summary["n_total_frames"] >= 5

"""MD/ML science KPI: |ΔE| below accuracy_threshold_hartree with classical H2 Morse."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from tests.helpers.paths import configs_path

pytestmark = pytest.mark.l1_md_ml
pytest.importorskip("jax_md")


def _mock_label_base(experiment_yaml, **kwargs):
    from qchem_stack.md_bridge.active_learning import mock_labeling_result

    del experiment_yaml, kwargs
    return mock_labeling_result(
        [1, 1],
        [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.5]]],
    )


def _mock_label_geoms(experiment_yaml, extra_coordinates_bohr, **kwargs):
    from qchem_stack.md_bridge.active_learning import mock_labeling_result

    del experiment_yaml, kwargs
    return mock_labeling_result(
        [1, 1],
        [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        extra_coordinates_bohr,
    )


def _mock_predict(handle, positions_bohr, atomic_numbers, **kwargs):
    import numpy as np

    del handle, kwargs
    n = len(atomic_numbers)
    return -1.12, np.zeros((n, 3), dtype=float)


def _mock_traj(handle, initial_positions_bohr, atomic_numbers, **kwargs):
    import numpy as np

    from qchem_stack.md_bridge.qmlff_md import JaxMdTrajectory

    del handle, kwargs
    base = np.asarray(initial_positions_bohr, dtype=float)
    stretched = base.copy()
    stretched[1, 2] += 0.05
    return JaxMdTrajectory(
        positions_bohr=[base, stretched],
        energies_hartree=[-1.12, -1.11],
        temperatures_K=[300.0, 300.0],
        times_ps=[0.0, 0.001],
        atomic_numbers=list(atomic_numbers),
        meta={"mock": True},
    )


def test_md_validation_five_rounds_meets_accuracy_threshold(tmp_path: Path) -> None:
    from qchem_stack.md_bridge import MdValidationLoopConfig, run_md_validation_loop

    exp_yaml = configs_path("example_h2.yaml")
    loop_cfg = MdValidationLoopConfig(
        max_rounds=5,
        force_field_backend="classical_h2",
        energy_tolerance_hartree=0.1,
        energy_normalization="none",
        n_candidate_frames=1,
        add_top_k_per_round=1,
        label_energy_reference="variational",
        validation_energy_reference="variational",
        validation_theory_level="full_pipeline",
        label_top_theory_level="full_pipeline",
        md_n_steps=6,
        md_save_stride=3,
        n_epochs_per_round=2,
        write_per_round_extxyz=False,
    )
    out_dir = tmp_path / "md_kpi"

    with (
        patch(
            "qchem_stack.md_bridge.md_validation_loop.label_base_geometry_only",
            side_effect=_mock_label_base,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.label_geometries_with_pipeline",
            side_effect=_mock_label_geoms,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.run_jaxmd_trajectory",
            side_effect=_mock_traj,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.predict_energy_forces_hartree",
            side_effect=_mock_predict,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.qmlff_handle_to_qmef_frame",
            side_effect=lambda handle, **kw: {
                "energy_hartree": -1.12,
                "positions_bohr": kw.get("positions_bohr"),
                "atomic_numbers": kw.get("atomic_numbers"),
            },
        ),
    ):
        summary = run_md_validation_loop(
            exp_yaml,
            config=loop_cfg,
            output_dir=out_dir,
            accuracy_threshold_hartree=0.1,
        )

    assert summary["science_kpi_met"] is True
    assert summary["max_abs_delta_hartree"] < summary["accuracy_threshold_hartree"]
    assert len(summary["rounds"]) >= 1


def test_md_validation_runs_five_rounds_when_below_loop_tolerance(tmp_path: Path) -> None:
    from qchem_stack.md_bridge import MdValidationLoopConfig, run_md_validation_loop

    exp_yaml = configs_path("example_h2.yaml")
    loop_cfg = MdValidationLoopConfig(
        max_rounds=5,
        force_field_backend="classical_h2",
        energy_tolerance_hartree=1e-6,
        energy_normalization="none",
        n_candidate_frames=1,
        add_top_k_per_round=1,
        label_top_theory_level="hf_scf",
        validation_theory_level="hf_scf",
        label_energy_reference="scf",
        validation_energy_reference="scf",
        md_n_steps=4,
        md_save_stride=2,
        n_epochs_per_round=1,
        write_per_round_extxyz=False,
    )
    out_dir = tmp_path / "md_five_rounds"

    with (
        patch(
            "qchem_stack.md_bridge.md_validation_loop.label_base_geometry_only",
            side_effect=_mock_label_base,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.label_geometries_with_pipeline",
            side_effect=_mock_label_geoms,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.run_jaxmd_trajectory",
            side_effect=_mock_traj,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.predict_energy_forces_hartree",
            side_effect=_mock_predict,
        ),
        patch(
            "qchem_stack.md_bridge.md_loop_rounds.qmlff_handle_to_qmef_frame",
            side_effect=lambda handle, **kw: {
                "energy_hartree": -1.12,
                "positions_bohr": kw.get("positions_bohr"),
                "atomic_numbers": kw.get("atomic_numbers"),
            },
        ),
    ):
        summary = run_md_validation_loop(
            exp_yaml,
            config=loop_cfg,
            output_dir=out_dir,
            accuracy_threshold_hartree=0.1,
        )

    assert len(summary["rounds"]) == 5

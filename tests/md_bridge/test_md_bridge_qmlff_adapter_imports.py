"""Soft-import / surface stability tests for the new qmlff_adapter module.

These tests **must pass even when ``qmlff`` and ``jax_md`` are not installed** —
that is the entire point of soft-import: ``qchem_stack`` callers can ``import``
the bridge even on a vanilla install and only pay the dependency cost if they
actually exercise the QML-FF code paths.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.l1_md_ml


def test_qmlff_adapter_module_imports_without_qmlff() -> None:
    """Importing qmlff_adapter must not require qmlff itself to be installed."""
    from qchem_stack.md_bridge import qmlff_adapter

    assert hasattr(qmlff_adapter, "build_qmlff_model_from_preset")
    assert hasattr(qmlff_adapter, "run_jaxmd_trajectory")
    assert hasattr(qmlff_adapter, "QmlffModelHandle")
    assert hasattr(qmlff_adapter, "JaxMdTrajectory")
    assert hasattr(qmlff_adapter, "atomic_number_to_symbol")


def test_md_bridge_init_reexports_new_surface() -> None:
    """``__init__`` must keep all legacy names AND export the new ones."""
    import qchem_stack.md_bridge as bridge

    legacy = {
        "QMFrame",
        "QMEFDataset",
        "ForceFieldTrainerProtocol",
        "TrainedModelArtifact",
        "StubTorchMLIPTrainer",
        "export_extended_xyz",
        "write_hdf5_stub",
        "write_nequip_yaml_stub",
        "write_mace_yaml_stub",
    }
    new = {
        "EnergyReference",
        "TheoryLevel",
        "LabelingFailure",
        "LabelingResult",
        "label_base_geometry_only",
        "label_geometries_with_pipeline",
        "merge_qmef_datasets",
        "QmlffModelHandle",
        "JaxMdTrajectory",
        "build_force_field_handle",
        "build_qmlff_model_from_preset",
        "build_qmlff_model_quantum_ff",
        "build_qmlff_model_angle",
        "build_qmp_h2_model",
        "train_force_field_on_qmef",
        "train_qmlff_on_qmef",
        "ForceFieldBackend",
        "ClassicalH2MorseHandle",
        "build_classical_h2_handle",
        "train_classical_h2_on_qmef",
        "predict_energy_forces_hartree",
        "run_jaxmd_trajectory",
        "select_geometries_from_trajectory",
        "trajectory_to_extxyz",
        "qmlff_handle_to_qmef_frame",
        "atomic_number_to_symbol",
        "symbol_to_atomic_number",
        "Ensemble",
        "MdValidationLoopConfig",
        "FrameValidationRecord",
        "MdValidationRoundLog",
        "run_md_validation_loop",
    }
    available = set(bridge.__all__)
    missing_legacy = legacy - available
    missing_new = new - available
    assert not missing_legacy, f"legacy md_bridge surface lost: {missing_legacy}"
    assert not missing_new, f"new md_bridge surface missing: {missing_new}"
    # All names in __all__ must actually be importable
    for name in legacy | new:
        assert getattr(bridge, name, None) is not None, f"{name} not bound in md_bridge"


def test_md_validation_loop_config_yaml_roundtrip(tmp_path) -> None:
    """``MdValidationLoopConfig.from_yaml`` should ignore unknown keys gracefully."""
    from qchem_stack.md_bridge import MdValidationLoopConfig

    yaml_path = tmp_path / "loop.yaml"
    yaml_path.write_text(
        "max_rounds: 3\n"
        "n_seed_geometries: 1\n"
        "energy_tolerance_hartree: 0.0005\n"
        "md_n_steps: 50\n"
        "md_save_stride: 5\n"
        "qmlff_species_list: [H]\n"
        "this_field_does_not_exist: 42\n",
        encoding="utf-8",
    )
    cfg = MdValidationLoopConfig.from_yaml(yaml_path)
    assert cfg.max_rounds == 3
    assert cfg.n_seed_geometries == 1
    assert cfg.md_n_steps == 50
    assert cfg.qmlff_species_list == ["H"]
    # Unknown field must not become an attribute
    assert not hasattr(cfg, "this_field_does_not_exist")


def test_example_h2_qmlff_md_yaml_loads() -> None:
    """Shipped H2 loop YAML should parse the new seed/MD/preset knobs."""
    from pathlib import Path

    import numpy as np

    from qchem_stack.md_bridge.md_validation_loop import (
        MdValidationLoopConfig,
        _bond_stretch_geometries,
    )

    repo = Path(__file__).resolve().parents[2]
    cfg = MdValidationLoopConfig.from_yaml(repo / "configs/example_h2_qmlff_md.yaml")
    assert cfg.force_field_backend == "qmlff_preset"
    assert cfg.lr_scheduler == "constant"
    assert cfg.warm_start_params_only is True
    assert cfg.force_weight == 10.0
    assert cfg.qmlff_builder_overrides == {"n_qubits": 6, "n_layers": 2}
    assert cfg.seed_mode == "bond_stretch"
    assert cfg.md_init_frame == "base"
    assert cfg.n_epochs_per_round == 50
    assert cfg.label_energy_reference == "scf"

    geoms = _bond_stretch_geometries(
        np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]], dtype=np.float64),
        n=3,
        r_min_bohr=0.8,
        r_max_bohr=2.0,
    )
    assert len(geoms) == 3
    assert np.linalg.norm(np.asarray(geoms[0][1]) - np.asarray(geoms[0][0])) == pytest.approx(
        0.8, rel=1e-6
    )


def test_example_h2_qnn_native_yaml_loads() -> None:
    from pathlib import Path

    from qchem_stack.md_bridge import MdValidationLoopConfig

    repo = Path(__file__).resolve().parents[2]
    cfg = MdValidationLoopConfig.from_yaml(repo / "configs/example_h2_qnn_native_md.yaml")
    assert cfg.force_field_backend == "qmlff_quantum"
    assert cfg.energy_normalization == "subtract_mean"
    assert cfg.grad_clip == 1.0
    assert cfg.qmlff_builder_overrides == {
        "n_qubits": 5,
        "n_layers": 4,
        "encoding_type": "angle",
    }
    assert cfg.warm_start is False
    assert cfg.n_epochs_per_round == 80
    assert cfg.batch_size == 4


def test_phase_yaml_configs_load() -> None:
    from pathlib import Path

    from qchem_stack.md_bridge import MdValidationLoopConfig

    repo = Path(__file__).resolve().parents[2]
    qmp = MdValidationLoopConfig.from_yaml(repo / "configs/example_h2_qmp_md.yaml")
    assert qmp.force_field_backend == "qmlff_qmp_h2"
    classical = MdValidationLoopConfig.from_yaml(repo / "configs/example_h2_classical_md.yaml")
    assert classical.force_field_backend == "classical_h2"


def test_qmlff_adapter_raises_friendly_when_qmlff_missing(monkeypatch) -> None:
    """If qmlff is not importable, the facade must raise ImportError with a hint."""
    import importlib
    import sys

    # Hide qmlff if present, hide it otherwise: simulate "not installed".
    monkeypatch.setitem(sys.modules, "qmlff", None)

    # Re-import the adapter so the cached _require_qmlff sees the stubbed module.
    from qchem_stack.md_bridge import qmlff_adapter

    importlib.reload(qmlff_adapter)
    with pytest.raises(ImportError) as excinfo:
        qmlff_adapter._require_qmlff()
    assert "pip install -e" in str(excinfo.value)


def test_select_geometries_from_trajectory_handles_short_runs() -> None:
    """select_geometries_from_trajectory works without qmlff installed."""
    import numpy as np

    from qchem_stack.md_bridge import JaxMdTrajectory, select_geometries_from_trajectory

    traj = JaxMdTrajectory(
        positions_bohr=[
            np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]),
            np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.41]]),
            np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.42]]),
        ],
        energies_hartree=[-1.0, -1.001, -1.002],
        temperatures_K=[300.0, 305.0, 295.0],
        times_ps=[0.0, 0.005, 0.010],
        atomic_numbers=[1, 1],
        meta={},
    )
    picks = select_geometries_from_trajectory(traj, n_candidates=2)
    assert len(picks) == 2
    assert all(len(g) == 2 and len(g[0]) == 3 for g in picks)


def test_merge_qmef_datasets_deduplicates_by_geometry() -> None:
    from qchem_stack.md_bridge import QMEFDataset, QMFrame, merge_qmef_datasets

    fr1 = QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        energy_hartree=-1.0,
    )
    fr2 = QMFrame(
        atomic_numbers=[1, 1],
        # Same geometry within 4 decimals
        positions_bohr=[[0.00001, 0.0, 0.0], [0.0, 0.0, 1.40004]],
        energy_hartree=-1.0001,
    )
    fr3 = QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.5]],
        energy_hartree=-0.99,
    )
    ds_a = QMEFDataset(frames=[fr1])
    ds_b = QMEFDataset(frames=[fr2, fr3])
    merged = merge_qmef_datasets(ds_a, ds_b, dedupe_decimals=4)
    assert len(merged.frames) == 2  # fr1 + fr3, fr2 deduped

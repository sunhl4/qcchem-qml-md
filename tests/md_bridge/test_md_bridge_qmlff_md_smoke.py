"""Optional smoke for the full QML-FF + JAX-MD adapter path.

Skipped on installs that don't have ``qmlff`` and ``jax-md`` available; safe to
run locally after ``pip install -e /path/to/QML-FF jax-md``.
"""

from __future__ import annotations

import numpy as np
import pytest

from tests.helpers.paths import configs_path

pytestmark = pytest.mark.l1_md_ml

pytest.importorskip("qmlff")
pytest.importorskip("jax_md")


@pytest.fixture(scope="module")
def small_qmef_dataset():
    """Two tiny H2-like frames for warm-start sanity (Bohr / Hartree / Ha/Bohr)."""
    from qchem_stack.md_bridge import QMEFDataset, QMFrame

    fr1 = QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
        energy_hartree=-1.0,
        forces_hartree_bohr=[[0.0, 0.0, -0.001], [0.0, 0.0, 0.001]],
        method_tag="synthetic-baseline",
    )
    fr2 = QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.45]],
        energy_hartree=-0.998,
        forces_hartree_bohr=[[0.0, 0.0, -0.002], [0.0, 0.0, 0.002]],
        method_tag="synthetic-stretched",
    )
    return QMEFDataset(frames=[fr1, fr2], provenance_yaml="qmlff_md_smoke: synthetic\n")


def test_build_qmlff_model_handle_initialises_params():
    from qchem_stack.md_bridge import build_qmlff_model_from_preset

    handle = build_qmlff_model_from_preset(["H"], preset="atomic_amplitude")
    assert handle.species_list == ["H"]
    assert handle.params, "QML-FF should return non-empty initial params"
    idx = handle.species_indices([1, 1])
    assert idx.tolist() == [0, 0]


def test_build_qmlff_from_preset_resolves_auto_device():
    """Presets use device_name=auto; builder must resolve before qml.device()."""
    import pennylane as qml

    from qchem_stack.md_bridge import build_qmlff_model_from_preset

    with pytest.raises(Exception, match="auto"):
        qml.device("auto", wires=2)

    handle = build_qmlff_model_from_preset(["H"], preset="atomic_amplitude")
    assert handle.model.dev.name != "auto"


def test_predict_energy_forces_hartree_units_roundtrip(small_qmef_dataset):
    from qchem_stack.md_bridge import (
        build_qmlff_model_from_preset,
        predict_energy_forces_hartree,
    )

    handle = build_qmlff_model_from_preset(["H"], preset="atomic_amplitude")
    e_h, f_hb = predict_energy_forces_hartree(
        handle,
        positions_bohr=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]),
        atomic_numbers=[1, 1],
    )
    assert np.isfinite(e_h)
    assert f_hb.shape == (2, 3)
    assert np.all(np.isfinite(f_hb))


def test_train_qmlff_on_qmef_runs_one_epoch(small_qmef_dataset, tmp_path):
    from qchem_stack.md_bridge import (
        build_qmlff_model_from_preset,
        train_qmlff_on_qmef,
    )

    handle = build_qmlff_model_from_preset(["H"], preset="atomic_amplitude")
    train_qmlff_on_qmef(
        handle,
        small_qmef_dataset,
        n_epochs=1,
        batch_size=1,
        learning_rate=1e-3,
        force_weight=1.0,
        checkpoint_dir=tmp_path / "ckpt",
        warm_start=False,
        early_stopping=False,
        seed=0,
    )
    assert handle.train_meta["n_train_frames"] == 2
    assert handle.step >= 1


def test_run_jaxmd_trajectory_returns_bohr_frames(small_qmef_dataset, tmp_path):
    from qchem_stack.md_bridge import (
        build_qmlff_model_from_preset,
        run_jaxmd_trajectory,
        train_qmlff_on_qmef,
        trajectory_to_extxyz,
    )

    handle = build_qmlff_model_from_preset(["H"], preset="atomic_amplitude")
    # Train one epoch so jit cache is warm and parameters aren't pathological.
    train_qmlff_on_qmef(
        handle,
        small_qmef_dataset,
        n_epochs=1,
        batch_size=1,
        learning_rate=1e-3,
        force_weight=1.0,
        checkpoint_dir=tmp_path / "ckpt",
        warm_start=False,
        seed=0,
    )

    traj = run_jaxmd_trajectory(
        handle,
        initial_positions_bohr=np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]),
        atomic_numbers=[1, 1],
        n_steps=10,
        dt_fs=0.25,
        temperature_K=300.0,
        ensemble="nvt_langevin",
        save_stride=5,
        seed=1,
    )

    assert len(traj.positions_bohr) >= 1
    assert len(traj.energies_hartree) == len(traj.positions_bohr)
    assert traj.atomic_numbers == [1, 1]
    assert all(p.shape == (2, 3) for p in traj.positions_bohr)

    # extxyz dump should be writeable + non-empty.
    out_path = tmp_path / "traj.xyz"
    trajectory_to_extxyz(traj, out_path)
    text = out_path.read_text(encoding="utf-8")
    assert text.lstrip().startswith("2")
    assert "energy_hartree" in text


@pytest.mark.pyscf
def test_full_md_validation_loop_runs_one_round_on_h2(tmp_path):
    """Cheap end-to-end loop on H2 — depends on PySCF as well as QML-FF/jax-md."""
    pytest.importorskip("pyscf")

    from qchem_stack.md_bridge import (
        MdValidationLoopConfig,
        run_md_validation_loop,
    )

    yaml_path = configs_path("example_h2.yaml")
    if not yaml_path.is_file():
        pytest.skip(f"missing {yaml_path}")

    cfg = MdValidationLoopConfig(
        max_rounds=1,
        n_seed_geometries=0,
        n_epochs_per_round=1,
        batch_size=1,
        learning_rate=1e-3,
        force_weight=1.0,
        md_n_steps=4,
        md_save_stride=2,
        md_dt_fs=0.25,
        md_temperature_K=300.0,
        n_candidate_frames=2,
        add_top_k_per_round=1,
        energy_tolerance_hartree=1.0,  # huge tol → almost certainly "converged" in smoke
        label_energy_reference="scf",
        label_screening_theory_level="hf_scf",
        label_top_theory_level="hf_scf",
        include_hf_nuclear_gradient=False,
        write_per_round_extxyz=True,
        qmlff_species_list=["H"],
        seed=0,
        md_seed=0,
    )
    summary = run_md_validation_loop(yaml_path, config=cfg, output_dir=tmp_path / "out")
    assert summary["rounds"], "loop should emit at least one round log"
    r0 = summary["rounds"][0]
    assert r0["n_md_frames_sampled"] >= 1
    # train_final.xyz and per-round artefacts should land in the output dir.
    assert (tmp_path / "out" / "train_final.xyz").is_file()
    assert (tmp_path / "out" / "md_validation_summary.json").is_file()

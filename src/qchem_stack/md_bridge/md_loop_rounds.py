"""Single-round train / MD / label logic for the MD validation loop."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.md_bridge.exporter import export_extended_xyz
from qchem_stack.md_bridge.md_loop_config import (
    FrameValidationRecord,
    MdValidationLoopConfig,
    MdValidationRoundLog,
)
from qchem_stack.md_bridge.md_loop_geometry import (
    bond_stretch_geometries,
    jitter_geometries,
    make_seed_geometries,
)
from qchem_stack.md_bridge.md_loop_summary import write_round_metrics
from qchem_stack.md_bridge.qchem_labeler import (
    EnergyReference,
    LabelingResult,
    TheoryLevel,
    label_geometries_with_pipeline,
    merge_qmef_datasets,
)
from qchem_stack.md_bridge.qmlff_adapter import (
    JaxMdTrajectory,
    QmlffModelHandle,
    predict_energy_forces_hartree,
    qmlff_handle_to_qmef_frame,
    run_jaxmd_trajectory,
    select_geometries_from_trajectory,
    train_force_field_on_qmef,
    trajectory_to_extxyz,
)
from qchem_stack.md_bridge.schema import QMEFDataset

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

logger = logging.getLogger(__name__)


def compute_training_energy_shift_hartree(
    handle: QmlffModelHandle,
    dataset: QMEFDataset,
) -> float:
    """Mean ``E_qchem - E_qml`` on the current training set (constant-offset calibration)."""
    if not dataset.frames:
        return 0.0
    deltas: list[float] = []
    for fr in dataset.frames:
        pos = np.asarray(fr.positions_bohr, dtype=np.float64)
        zs = [int(z) for z in fr.atomic_numbers]
        e_qml, _ = predict_energy_forces_hartree(handle, positions_bohr=pos, atomic_numbers=zs)
        deltas.append(float(fr.energy_hartree) - float(e_qml))
    return float(np.mean(deltas))


def build_frame_records(
    *,
    handle: QmlffModelHandle,
    candidate_geoms: list[list[list[float]]],
    atomic_numbers: Sequence[int],
    screen_result: LabelingResult,
    tolerance_hartree: float,
    label_theory_level: str,
    trajectory: JaxMdTrajectory,
    energy_shift_hartree: float = 0.0,
    energy_reference_used: str = "variational",
) -> tuple[list[FrameValidationRecord], dict[int, dict[str, Any]]]:
    """Build per-MD-frame |ΔE| records and a JSON-friendly debug mapping."""
    # Map from index-in-candidate_geoms to QMEF frame coming back from labeling.
    # screen_result.dataset.frames[0] is the base; extras start at index 1.
    qchem_by_idx: dict[int, Any] = {}
    failed_idx = {fail.index for fail in screen_result.failures}
    extra_iter = iter(screen_result.dataset.frames[1:])
    for i in range(len(candidate_geoms)):
        if i in failed_idx:
            qchem_by_idx[i] = None
            continue
        try:
            qchem_by_idx[i] = next(extra_iter)
        except StopIteration:
            qchem_by_idx[i] = None

    # Time per candidate ≈ saved_index_in_trajectory * dt_fs * save_stride.
    # `select_geometries_from_trajectory` skips the initial frame and picks
    # `n_candidate_frames` evenly across the saved frames; reconstruct a
    # plausible time stamp by matching positions back to the trajectory.
    time_lookup = trajectory_time_lookup(trajectory)

    records: list[FrameValidationRecord] = []
    debug: dict[int, dict[str, Any]] = {}
    zs = [int(z) for z in atomic_numbers]
    for i, geom in enumerate(candidate_geoms):
        pos_bohr = np.asarray(geom, dtype=np.float64)
        e_qml, _ = predict_energy_forces_hartree(handle, positions_bohr=pos_bohr, atomic_numbers=zs)
        qchem_frame = qchem_by_idx.get(i)
        if qchem_frame is None:
            e_ref = float("nan")
            delta = float("nan")
            abs_delta = float("inf")
            delta_raw = float("nan")
            abs_delta_raw = float("inf")
        else:
            e_ref = float(qchem_frame.energy_hartree)
            delta_raw = float(e_qml) - e_ref
            abs_delta_raw = abs(delta_raw)
            e_qml_cal = float(e_qml) + float(energy_shift_hartree)
            delta = e_qml_cal - e_ref
            abs_delta = abs(delta)
        rec = FrameValidationRecord(
            frame_index=i,
            time_ps=float(time_lookup(pos_bohr)),
            energy_qml_hartree=float(e_qml),
            energy_qchem_hartree=float(e_ref),
            delta_hartree=float(delta) if delta == delta else float("nan"),  # NaN-safe
            abs_delta_hartree=float(abs_delta),
            converged=bool(abs_delta < tolerance_hartree),
            theory_level=str(label_theory_level),
            energy_reference_used=str(energy_reference_used),
            delta_hartree_raw=float(delta_raw),
            abs_delta_hartree_raw=float(abs_delta_raw),
        )
        records.append(rec)
        debug[i] = {
            "qml_prediction": qmlff_handle_to_qmef_frame(
                handle, positions_bohr=pos_bohr, atomic_numbers=zs
            ),
            "qchem_reference": (
                qchem_frame.model_dump(mode="json") if qchem_frame is not None else None
            ),
        }
    return records, debug


def trajectory_time_lookup(trajectory: JaxMdTrajectory):
    """Return a callable that maps a geometry → its approximate ``time_ps``.

    Implementation: nearest-neighbor (Frobenius) match against trajectory.positions_bohr.
    """
    arr = np.stack(trajectory.positions_bohr, axis=0) if trajectory.positions_bohr else None
    times = np.asarray(trajectory.times_ps, dtype=np.float64)

    def _lookup(pos: np.ndarray) -> float:
        if arr is None or arr.size == 0:
            return float("nan")
        diffs = arr - np.asarray(pos, dtype=np.float64)[None, ...]
        norms = np.linalg.norm(diffs.reshape(arr.shape[0], -1), axis=-1)
        return float(times[int(np.argmin(norms))])

    return _lookup


def _select_upgrade_dataset(
    *,
    cfg: MdValidationLoopConfig,
    records: list[FrameValidationRecord],
    candidate_geoms: list[Any],
    val_theory: TheoryLevel,
    val_energy_ref: EnergyReference,
    screen_result: LabelingResult,
    exp_yaml: Path,
) -> QMEFDataset:
    """Pick the top-K worst frames and produce their high-fidelity training labels.

    When the screening label already matches the target theory/reference we reuse
    the screening frames; otherwise we re-label the selected geometries at the
    higher-fidelity level. Returns an empty dataset when nothing is selected.
    """
    upgrade_records = sorted(records, key=lambda r: r.abs_delta_hartree, reverse=True)[
        : max(0, int(cfg.add_top_k_per_round))
    ]
    upgrade_geoms = [candidate_geoms[r.frame_index] for r in upgrade_records]
    if not upgrade_geoms:
        return QMEFDataset(frames=[])

    if cfg.label_top_theory_level == val_theory and (
        cfg.label_energy_reference == val_energy_ref or cfg.validation_energy_reference is not None
    ):
        return QMEFDataset(
            frames=[
                screen_result.dataset.frames[1 + r.frame_index]
                for r in upgrade_records
                if (1 + r.frame_index) < len(screen_result.dataset.frames)
            ]
        )

    top_result = label_geometries_with_pipeline(
        exp_yaml,
        extra_coordinates_bohr=upgrade_geoms,
        energy_reference=cfg.label_energy_reference,
        theory_level=cfg.label_top_theory_level,
        include_hf_nuclear_gradient=cfg.include_hf_nuclear_gradient,
        failure_isolation=True,
    )
    # Strip the duplicated base frame returned by labeling.
    top_extras = top_result.dataset.frames[1:] if top_result.dataset.frames else []
    return QMEFDataset(frames=top_extras)


def run_validation_round(
    *,
    round_i: int,
    cfg: MdValidationLoopConfig,
    exp_yaml: Path,
    out: Path,
    handle: QmlffModelHandle,
    dataset: QMEFDataset,
) -> tuple[QMEFDataset, MdValidationRoundLog, bool, bool]:
    """Run one active-learning round: train → MD → label → merge.

    Returns:
        Updated dataset, round log, whether all frames converged, and whether
        the outer loop should stop early (no MD candidates).
    """
    logger.info("---- MD validation round %s/%s ----", round_i, cfg.max_rounds)
    n_before = len(dataset.frames)

    train_force_field_on_qmef(
        handle,
        dataset,
        n_epochs=cfg.n_epochs_per_round,
        batch_size=cfg.batch_size,
        learning_rate=cfg.learning_rate,
        force_weight=cfg.force_weight,
        lr_scheduler=cfg.lr_scheduler,
        checkpoint_dir=out / "qmlff_checkpoints" / f"round_{round_i:02d}",
        checkpoint_save_freq=cfg.qmlff_checkpoint_save_freq,
        warm_start=cfg.warm_start,
        warm_start_params_only=cfg.warm_start_params_only,
        energy_normalization=cfg.energy_normalization,
        grad_clip=cfg.grad_clip,
        seed=cfg.seed + round_i,
    )

    energy_shift = compute_training_energy_shift_hartree(handle, dataset)
    handle.train_meta["validation_energy_shift_hartree"] = float(energy_shift)

    # Default ``md_init_frame=last`` keeps AL near strained configs; use
    # ``base`` to start every MD from the equilibrium geometry (recommended
    # for H2 while the force field is still immature).
    init_frame = dataset.frames[0] if cfg.md_init_frame == "base" else dataset.frames[-1]
    init_pos_bohr = np.asarray(init_frame.positions_bohr, dtype=np.float64)
    init_zs = [int(z) for z in init_frame.atomic_numbers]

    trajectory = run_jaxmd_trajectory(
        handle,
        initial_positions_bohr=init_pos_bohr,
        atomic_numbers=init_zs,
        n_steps=cfg.md_n_steps,
        dt_fs=cfg.md_dt_fs,
        temperature_K=cfg.md_temperature_K,
        ensemble=cfg.md_ensemble,
        save_stride=cfg.md_save_stride,
        seed=cfg.md_seed + round_i,
        cutoff_ang=cfg.cutoff_ang,
        max_neighbors=cfg.max_neighbors,
    )
    if cfg.write_per_round_extxyz:
        trajectory_to_extxyz(trajectory, out / f"md_round_{round_i}.xyz")

    candidate_geoms = select_geometries_from_trajectory(
        trajectory,
        n_candidates=cfg.n_candidate_frames,
        skip_initial=cfg.validation_skip_initial_md_frame,
    )
    if not candidate_geoms:
        logger.warning(
            "round %s: no MD frames available for validation (n_steps=%s, save_stride=%s);"
            " stopping loop",
            round_i,
            cfg.md_n_steps,
            cfg.md_save_stride,
        )
        log = MdValidationRoundLog(
            round_index=round_i,
            n_train_before=n_before,
            n_train_after=n_before,
            n_md_frames_sampled=0,
            max_abs_delta_hartree=float("nan"),
            mean_abs_delta_hartree=float("nan"),
            converged=False,
            training_metrics=dict(handle.train_meta),
        )
        return dataset, log, False, True

    val_energy_ref: EnergyReference = cfg.validation_energy_reference or cfg.label_energy_reference
    val_theory: TheoryLevel = cfg.validation_theory_level or cfg.label_top_theory_level

    # Score every MD candidate with the same energy reference as training labels.
    screen_result: LabelingResult = label_geometries_with_pipeline(
        exp_yaml,
        extra_coordinates_bohr=candidate_geoms,
        energy_reference=val_energy_ref,
        theory_level=val_theory,
        include_hf_nuclear_gradient=cfg.include_hf_nuclear_gradient,
        failure_isolation=True,
    )

    # Per-frame delta vs QML-FF (E_ref aligned with validation_energy_reference).
    records, by_index = build_frame_records(
        handle=handle,
        candidate_geoms=candidate_geoms,
        atomic_numbers=init_zs,
        screen_result=screen_result,
        tolerance_hartree=cfg.energy_tolerance_hartree,
        label_theory_level=val_theory,
        trajectory=trajectory,
        energy_shift_hartree=energy_shift,
        energy_reference_used=val_energy_ref,
    )

    # If all converged → stop.
    max_abs = max((r.abs_delta_hartree for r in records), default=float("nan"))
    mean_abs = float(np.mean([r.abs_delta_hartree for r in records])) if records else float("nan")
    all_converged = bool(records) and all(r.converged for r in records)

    # Choose top-K geometries to upgrade to the higher-fidelity label
    # (or just use the screening labels when label_top_theory_level matches).
    upgrade_dataset = _select_upgrade_dataset(
        cfg=cfg,
        records=records,
        candidate_geoms=candidate_geoms,
        val_theory=val_theory,
        val_energy_ref=val_energy_ref,
        screen_result=screen_result,
        exp_yaml=exp_yaml,
    )

    if upgrade_dataset.frames:
        dataset = merge_qmef_datasets(dataset, upgrade_dataset, dedupe_decimals=cfg.dedupe_decimals)

    n_after = len(dataset.frames)
    log = MdValidationRoundLog(
        round_index=round_i,
        n_train_before=n_before,
        n_train_after=n_after,
        n_md_frames_sampled=len(candidate_geoms),
        max_abs_delta_hartree=float(max_abs),
        mean_abs_delta_hartree=float(mean_abs),
        converged=all_converged,
        training_metrics=dict(handle.train_meta),
        frames=records,
        failures=[asdict(f) for f in screen_result.failures],
    )

    if cfg.write_per_round_extxyz:
        export_extended_xyz(dataset, out / f"train_round_{round_i}.xyz")
    write_round_metrics(out, round_i, log, by_index)

    logger.info(
        "round %s: n_train %s → %s | max|ΔE|=%.6f Ha | mean|ΔE|=%.6f Ha | converged=%s",
        round_i,
        n_before,
        n_after,
        max_abs,
        mean_abs,
        all_converged,
    )

    return dataset, log, all_converged, False


__all__ = [
    "bond_stretch_geometries",
    "compute_training_energy_shift_hartree",
    "jitter_geometries",
    "make_seed_geometries",
    "run_validation_round",
]

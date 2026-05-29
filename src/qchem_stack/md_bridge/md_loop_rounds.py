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
    SeedMode,
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


def make_seed_geometries(
    base_bohr: np.ndarray,
    *,
    n: int,
    mode: SeedMode,
    sigma_bohr: float,
    bond_min_bohr: float,
    bond_max_bohr: float,
    rng: np.random.Generator,
) -> list[list[list[float]]]:
    if n <= 0:
        return []
    if mode == "bond_stretch":
        stretched = bond_stretch_geometries(
            base_bohr,
            n=n,
            r_min_bohr=bond_min_bohr,
            r_max_bohr=bond_max_bohr,
        )
        if stretched:
            return stretched
        logger.warning(
            "seed_mode=bond_stretch requested but geometry is not diatomic; falling back to jitter"
        )
    return jitter_geometries(base_bohr, n=n, sigma_bohr=sigma_bohr, rng=rng)


def jitter_geometries(
    base_bohr: np.ndarray,
    *,
    n: int,
    sigma_bohr: float,
    rng: np.random.Generator,
) -> list[list[list[float]]]:
    out: list[list[list[float]]] = []
    n_atoms = base_bohr.shape[0]
    for _ in range(int(n)):
        noise = rng.normal(scale=float(sigma_bohr), size=(n_atoms, 3))
        displaced = base_bohr + noise
        out.append(
            [
                [float(displaced[i, 0]), float(displaced[i, 1]), float(displaced[i, 2])]
                for i in range(n_atoms)
            ]
        )
    return out


def bond_stretch_geometries(
    base_bohr: np.ndarray,
    *,
    n: int,
    r_min_bohr: float,
    r_max_bohr: float,
) -> list[list[list[float]]]:
    """Scan bond lengths for a diatomic (H2-friendly); empty list if not 2-atom."""
    pos = np.asarray(base_bohr, dtype=np.float64)
    if pos.shape != (2, 3):
        return []
    delta = pos[1] - pos[0]
    bond = float(np.linalg.norm(delta))
    if bond <= 1.0e-8:
        return []
    axis = delta / bond
    center = 0.5 * (pos[0] + pos[1])
    radii = np.linspace(float(r_min_bohr), float(r_max_bohr), int(n))
    out: list[list[list[float]]] = []
    for r in radii:
        half = 0.5 * float(r)
        p0 = center - half * axis
        p1 = center + half * axis
        out.append(
            [
                [float(p0[0]), float(p0[1]), float(p0[2])],
                [float(p1[0]), float(p1[1]), float(p1[2])],
            ]
        )
    return out


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
        else:
            e_ref = float(qchem_frame.energy_hartree)
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
    )

    # If all converged → stop.
    max_abs = max((r.abs_delta_hartree for r in records), default=float("nan"))
    mean_abs = float(np.mean([r.abs_delta_hartree for r in records])) if records else float("nan")
    all_converged = bool(records) and all(r.converged for r in records)

    # Choose top-K geometries to upgrade to the higher-fidelity label
    # (or just use the screening labels when label_top_theory_level matches).
    upgrade_records = sorted(records, key=lambda r: r.abs_delta_hartree, reverse=True)[
        : max(0, int(cfg.add_top_k_per_round))
    ]
    upgrade_geoms = [candidate_geoms[r.frame_index] for r in upgrade_records]

    upgrade_dataset: QMEFDataset = QMEFDataset(frames=[])
    if upgrade_geoms:
        if cfg.label_top_theory_level == val_theory and (
            cfg.label_energy_reference == val_energy_ref
            or cfg.validation_energy_reference is not None
        ):
            upgrade_dataset = QMEFDataset(
                frames=[
                    screen_result.dataset.frames[1 + r.frame_index]
                    for r in upgrade_records
                    if (1 + r.frame_index) < len(screen_result.dataset.frames)
                ]
            )
        else:
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
            upgrade_dataset = QMEFDataset(frames=top_extras)

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

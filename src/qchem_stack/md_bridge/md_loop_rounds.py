"""Single-round train / MD / label logic for the MD validation loop."""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.md_bridge.exporter import export_extended_xyz
from qchem_stack.md_bridge.md_loop_config import (
    MdValidationLoopConfig,
    MdValidationRoundLog,
)
from qchem_stack.md_bridge.md_loop_frame_scoring import (
    _select_upgrade_dataset,
    build_frame_records,
    compute_training_energy_shift_hartree,
)
from qchem_stack.md_bridge.md_loop_geometry import (
    bond_stretch_geometries,
    classify_bond_regime,
    diatomic_bond_bohr,
    geometries_at_bond_lengths,
    jitter_geometries,
    make_seed_geometries,
    resolve_cutoff_bohr,
    resolve_max_train_bond_bohr,
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
    QmlffModelHandle,
    run_jaxmd_trajectory,
    select_geometries_from_trajectory,
    train_force_field_on_qmef,
    trajectory_to_extxyz,
)
from qchem_stack.md_bridge.schema import QMEFDataset

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


def run_validation_round(
    *,
    round_i: int,
    cfg: MdValidationLoopConfig,
    exp_yaml: Path,
    out: Path,
    handle: QmlffModelHandle,
    dataset: QMEFDataset,
    round_bonds_bohr: list[float] | None = None,
) -> tuple[QMEFDataset, MdValidationRoundLog, bool, bool]:
    """Run one active-learning round: train → MD → label → merge.

    Returns:
        Updated dataset, round log, whether all frames converged, and whether
        the outer loop should stop early (no MD candidates).
    """
    logger.info("---- MD validation round %s/%s ----", round_i, cfg.max_rounds)
    if round_bonds_bohr:
        logger.info(
            "round %s scheduled bond lengths (Bohr): %s",
            round_i,
            [round(float(r), 4) for r in round_bonds_bohr],
        )
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

    round_tol = cfg.resolve_round_tolerance(round_i)
    cutoff_b = resolve_cutoff_bohr(cfg.cutoff_ang)
    max_train_b = resolve_max_train_bond_bohr(
        max_train_bond_bohr=cfg.max_train_bond_bohr,
        cutoff_ang=cfg.cutoff_ang,
    )
    logger.info(
        "round %s tolerance=%.6g Ha | FF cutoff=%.3f Bohr (%.2f Å) | "
        "max_train_bond=%.3f Bohr | dissociation_mark=%.3f Bohr",
        round_i,
        round_tol,
        cutoff_b,
        float(cfg.cutoff_ang if cfg.cutoff_ang is not None else 6.0),
        max_train_b,
        float(cfg.dissociation_bond_bohr),
    )
    for i, geom in enumerate(candidate_geoms):
        bond = diatomic_bond_bohr(geom)
        regime = classify_bond_regime(
            bond,
            dissociation_bond_bohr=cfg.dissociation_bond_bohr,
            cutoff_bohr=cutoff_b,
        )
        logger.info(
            "round %s MD candidate[%s]: R=%.4f Bohr regime=%s "
            "(bound < %.2f ≤ dissociating ≤ cutoff %.2f < beyond_cutoff)",
            round_i,
            i,
            float(bond) if bond is not None else float("nan"),
            regime,
            float(cfg.dissociation_bond_bohr),
            cutoff_b,
        )

    # Per-frame delta vs QML-FF (E_ref aligned with validation_energy_reference).
    records, by_index = build_frame_records(
        handle=handle,
        candidate_geoms=candidate_geoms,
        atomic_numbers=init_zs,
        screen_result=screen_result,
        tolerance_hartree=round_tol,
        label_theory_level=val_theory,
        trajectory=trajectory,
        energy_shift_hartree=energy_shift,
        energy_reference_used=val_energy_ref,
    )

    # If all converged → stop (only meaningful vs current-stage tolerance).
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

    # Scheduled H–H bond lengths (PES coverage; complementary to seed scan).
    if round_bonds_bohr:
        base_pos = np.asarray(dataset.frames[0].positions_bohr, dtype=np.float64)
        bond_geoms = geometries_at_bond_lengths(base_pos, round_bonds_bohr)
        if bond_geoms:
            bond_result = label_geometries_with_pipeline(
                exp_yaml,
                extra_coordinates_bohr=bond_geoms,
                energy_reference=cfg.label_energy_reference,
                theory_level=cfg.label_top_theory_level,
                include_hf_nuclear_gradient=cfg.include_hf_nuclear_gradient,
                failure_isolation=True,
            )
            bond_extras = bond_result.dataset.frames[1:] if bond_result.dataset.frames else []
            if bond_extras:
                before_bonds = len(dataset.frames)
                dataset = merge_qmef_datasets(
                    dataset,
                    QMEFDataset(frames=bond_extras),
                    dedupe_decimals=cfg.dedupe_decimals,
                )
                logger.info(
                    "round %s bond schedule: +%s labeled geometries (failures=%s), dataset %s → %s",
                    round_i,
                    len(dataset.frames) - before_bonds,
                    len(bond_result.failures),
                    before_bonds,
                    len(dataset.frames),
                )

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

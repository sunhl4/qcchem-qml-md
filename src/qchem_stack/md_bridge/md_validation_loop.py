"""End-to-end "qchem ↔ QML-FF ↔ JAX-MD" active-learning loop.

High-level workflow
-------------------

::

    1. Cold-start: run qchem on the YAML's base geometry             ──┐
       → 1-frame :class:`QMEFDataset`                                  │
    2. (Optional) jitter N seed geometries around the base, label     │
       them with two-stage HF screening + top-k full pipeline.        │
       → seeded :class:`QMEFDataset`                                   │
    3. For round = 1 .. max_rounds:                                    │
         a. (warm-start) train QML-FF on the current dataset.          │ "few-shot
         b. Run JAX-MD trajectory using the QML-FF model.              │  or zero-shot
         c. Pick K candidate frames from the trajectory.               │  loop"
         d. Re-label every candidate with qchem (HF-cheap screening    │
            + full-pipeline top-k for the worst gaps).                 │
         e. Compute |E_qml − E_qchem|. If all gaps < tol → converged.  │
         f. Else merge top-k highest-gap frames into the dataset,      │
            persist round artefacts, loop.                            ──┘

The loop is **additive** to existing functionality: it does not modify
``run_pipeline_sync``, ``QMFrame``, ``QMEFDataset``, or any other public API.
``qmlff`` and ``jax_md`` are soft-imported via :mod:`.qmlff_adapter`.

See ``docs/qmlff_md_integration_说明.md`` for the full workflow tour and
``configs/example_h2_qmlff_md.yaml`` for a runnable starter config.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np

from qchem_stack.config import load_experiment_config
from qchem_stack.md_bridge.energy_reference import (
    prepare_loop_config,
    validate_loop_energy_consistency,
)
from qchem_stack.md_bridge.exporter import export_extended_xyz
from qchem_stack.md_bridge.md_loop_config import (
    Ensemble,
    FrameValidationRecord,
    MdValidationLoopConfig,
    MdValidationRoundLog,
)
from qchem_stack.md_bridge.md_loop_geometry import (
    classify_bond_regime,
    diatomic_bond_bohr,
    make_round_bond_schedule,
    resolve_cutoff_bohr,
    resolve_max_train_bond_bohr,
)
from qchem_stack.md_bridge.md_loop_rounds import (
    bond_stretch_geometries,
    jitter_geometries,
    make_seed_geometries,
    run_validation_round,
)
from qchem_stack.md_bridge.md_loop_summary import (
    build_md_validation_summary,
    write_md_validation_summary,
)
from qchem_stack.md_bridge.qchem_labeler import (
    label_base_geometry_only,
    label_geometries_with_pipeline,
    merge_qmef_datasets,
)
from qchem_stack.md_bridge.qmlff_adapter import (
    atomic_number_to_symbol,
    build_force_field_handle,
    train_force_field_on_qmef,
)

logger = logging.getLogger(__name__)


def run_md_validation_loop(
    experiment_yaml: str | Path,
    *,
    config: MdValidationLoopConfig | None = None,
    output_dir: str | Path = "results/qmlff_md_validation",
    accuracy_threshold_hartree: float | None = None,
) -> dict[str, Any]:
    """Run the full qchem → QML-FF → JAX-MD active-learning loop.

    Args:
        experiment_yaml: path to a qchem-stack experiment YAML (e.g.
            ``configs/example_h2.yaml``). Defines the chemistry side of the
            loop (molecule, basis, SCF/quantum/active space).
        config: :class:`MdValidationLoopConfig`; defaults are conservative
            (H2-friendly).
        output_dir: directory where per-round artefacts (extxyz / metrics
            JSON / trajectory) are written.

    Returns:
        A summary dict shaped::

            {
              "experiment_yaml": str,
              "output_dir": str,
              "config": <dataclass dict>,
              "n_total_frames": int,
              "rounds": [<MdValidationRoundLog as dict>, ...],
              "converged": bool,
            }

        The same dict is also written to ``<output_dir>/md_validation_summary.json``.

    Raises:
        :class:`ImportError`: when ``qmlff`` or ``jax_md`` is unavailable.
        :class:`qchem_stack.exceptions.PipelineError`: when the cold-start
            qchem labeling fails (no recovery possible).
    """
    cfg = prepare_loop_config(config or MdValidationLoopConfig())
    exp_yaml = Path(experiment_yaml)
    experiment_cfg = load_experiment_config(exp_yaml)
    validate_loop_energy_consistency(cfg, experiment_cfg, strict=True)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(int(cfg.seed))

    logger.info(
        "MD validation loop starting (experiment=%s, max_rounds=%s, "
        "md_steps=%s, n_candidate_frames=%s, tol_hartree=%g)",
        exp_yaml.name,
        cfg.max_rounds,
        cfg.md_n_steps,
        cfg.n_candidate_frames,
        cfg.energy_tolerance_hartree,
    )

    # ---- Cold start ------------------------------------------------------
    base_result = label_base_geometry_only(
        exp_yaml,
        energy_reference=cfg.label_energy_reference,
        theory_level=cfg.label_top_theory_level,
        include_hf_nuclear_gradient=cfg.include_hf_nuclear_gradient,
    )
    dataset = base_result.dataset
    logger.info(
        "cold-start labeling done: %s base frame(s); epistemic_bound=%r",
        len(dataset.frames),
        base_result.epistemic_bound[:80] + ("…" if len(base_result.epistemic_bound) > 80 else ""),
    )

    base_zs = list(dataset.frames[0].atomic_numbers)
    species_list = cfg.qmlff_species_list or sorted(
        {atomic_number_to_symbol(int(z)) for z in base_zs}
    )

    cutoff_b = resolve_cutoff_bohr(cfg.cutoff_ang)
    max_train_b = resolve_max_train_bond_bohr(
        max_train_bond_bohr=cfg.max_train_bond_bohr,
        cutoff_ang=cfg.cutoff_ang,
    )
    seed_max_eff = float(min(float(cfg.seed_bond_max_bohr), max_train_b))
    dissociation_policy: dict[str, Any] = {
        "cutoff_ang": float(cfg.cutoff_ang if cfg.cutoff_ang is not None else 6.0),
        "cutoff_bohr": cutoff_b,
        "dissociation_bond_bohr": float(cfg.dissociation_bond_bohr),
        "max_train_bond_bohr": max_train_b,
        "seed_bond_min_bohr": float(cfg.seed_bond_min_bohr),
        "seed_bond_max_bohr_requested": float(cfg.seed_bond_max_bohr),
        "seed_bond_max_bohr_effective": seed_max_eff,
        "note": (
            "Pre-dissociation (bound, R < dissociation_mark) and "
            "post-dissociation-but-within-cutoff (dissociating, "
            "dissociation_mark ≤ R ≤ cutoff) are both kept so the FF learns "
            "the bonded well and the dissociation asymptote while pair "
            "interactions are still evaluated. Frames with R > cutoff are "
            "rejected on MD merge because the neighbor list drops the pair."
        ),
    }
    logger.info(
        "dissociation/cutoff policy: cutoff=%.3f Bohr (%.2f Å), "
        "dissociation_mark=%.3f Bohr, max_train_bond=%.3f Bohr, "
        "seed scan=[%.3f, %.3f] Bohr (effective max clamped to cutoff policy)",
        cutoff_b,
        dissociation_policy["cutoff_ang"],
        float(cfg.dissociation_bond_bohr),
        max_train_b,
        float(cfg.seed_bond_min_bohr),
        seed_max_eff,
    )

    # ---- Optional seed augmentation -------------------------------------
    if cfg.n_seed_geometries > 0:
        base_pos = np.asarray(dataset.frames[0].positions_bohr, dtype=np.float64)
        seed_geoms = make_seed_geometries(
            base_pos,
            n=cfg.n_seed_geometries,
            mode=cfg.seed_mode,
            sigma_bohr=cfg.seed_jitter_bohr,
            bond_min_bohr=cfg.seed_bond_min_bohr,
            bond_max_bohr=seed_max_eff,
            rng=rng,
        )
        seed_result = label_geometries_with_pipeline(
            exp_yaml,
            extra_coordinates_bohr=seed_geoms,
            energy_reference=cfg.label_energy_reference,
            theory_level=cfg.label_top_theory_level,
            include_hf_nuclear_gradient=cfg.include_hf_nuclear_gradient,
            failure_isolation=True,
        )
        before = len(dataset.frames)
        dataset = merge_qmef_datasets(
            dataset, seed_result.dataset, dedupe_decimals=cfg.dedupe_decimals
        )
        logger.info(
            "seed augmentation: +%s frames (%s failures), dataset %s → %s",
            len(seed_result.dataset.frames) - 1,  # base re-included by merge dedupe
            len(seed_result.failures),
            before,
            len(dataset.frames),
        )

    if cfg.write_per_round_extxyz:
        export_extended_xyz(dataset, out / "train_round_0_initial.xyz")

    coverage = {"bound": 0, "dissociating": 0, "beyond_cutoff": 0, "unknown": 0}
    for fr in dataset.frames:
        bond = diatomic_bond_bohr(fr.positions_bohr)
        regime = classify_bond_regime(
            bond,
            dissociation_bond_bohr=cfg.dissociation_bond_bohr,
            cutoff_bohr=cutoff_b,
        )
        coverage[regime] = coverage.get(regime, 0) + 1
    dissociation_policy["seed_coverage_after_phase_a"] = coverage
    (out / "dissociation_cutoff_policy.json").write_text(
        json.dumps(dissociation_policy, indent=2),
        encoding="utf-8",
    )
    logger.info(
        "seed coverage after Phase A: bound=%s dissociating=%s beyond_cutoff=%s",
        coverage["bound"],
        coverage["dissociating"],
        coverage["beyond_cutoff"],
    )

    # ---- Build model -----------------------------------------------------
    handle = build_force_field_handle(
        species_list,
        backend=cfg.force_field_backend,
        preset=cfg.qmlff_preset,
        builder_overrides=cfg.qmlff_builder_overrides,
        qmp_h2_overrides=cfg.qmp_h2_overrides,
    )

    # ---- Phase B: pretrain on seed dataset (no MD / no AL) ----------------
    # Non-zero-shot path: quantum bond-scan labels must exist before this step.
    pretrain_meta: dict[str, Any] = {"enabled": False, "n_train_frames": len(dataset.frames)}
    if int(cfg.pretrain_epochs) > 0:
        if len(dataset.frames) < 2:
            logger.warning(
                "pretrain_epochs=%s but training set has only %s frame(s); "
                "increase n_seed_geometries for a real bond-scan pretrain",
                cfg.pretrain_epochs,
                len(dataset.frames),
            )
        logger.info(
            "==== Phase B: pretrain force field on quantum bond-scan set "
            "(%s frames, %s epochs; no MD) ====",
            len(dataset.frames),
            cfg.pretrain_epochs,
        )
        train_force_field_on_qmef(
            handle,
            dataset,
            n_epochs=int(cfg.pretrain_epochs),
            batch_size=cfg.batch_size,
            learning_rate=cfg.learning_rate,
            force_weight=cfg.force_weight,
            lr_scheduler=cfg.lr_scheduler,
            checkpoint_dir=out / "qmlff_checkpoints" / "pretrain",
            checkpoint_save_freq=cfg.qmlff_checkpoint_save_freq,
            warm_start=False,
            warm_start_params_only=True,
            energy_normalization=cfg.energy_normalization,
            grad_clip=cfg.grad_clip,
            seed=cfg.seed,
        )
        export_extended_xyz(dataset, out / "train_after_pretrain.xyz")
        pretrain_meta = {
            "enabled": True,
            "n_train_frames": len(dataset.frames),
            "pretrain_epochs": int(cfg.pretrain_epochs),
            "checkpoint_dir": str(out / "qmlff_checkpoints" / "pretrain"),
            "training_metrics": dict(handle.train_meta),
        }
        (out / "pretrain_metrics.json").write_text(
            json.dumps(pretrain_meta, indent=2),
            encoding="utf-8",
        )
        logger.info(
            "Phase B done: pretrained on %s frames → online learning will warm-start",
            len(dataset.frames),
        )

    round_logs: list[MdValidationRoundLog] = []
    converged = False

    round_bond_schedule: list[list[float]] = []
    if int(cfg.round_bonds_per_round) > 0:
        round_bond_schedule = make_round_bond_schedule(
            n_rounds=int(cfg.max_rounds),
            bonds_per_round=int(cfg.round_bonds_per_round),
            r_min_bohr=float(cfg.seed_bond_min_bohr),
            r_max_bohr=seed_max_eff,
            seed=int(cfg.seed) + 17,
        )
        logger.info(
            "per-round bond schedule enabled: %s bonds/round × %s rounds (range %.3f–%.3f Bohr)",
            cfg.round_bonds_per_round,
            cfg.max_rounds,
            cfg.seed_bond_min_bohr,
            cfg.seed_bond_max_bohr,
        )
        (out / "round_bond_schedule.json").write_text(
            json.dumps(
                {
                    "bonds_per_round": int(cfg.round_bonds_per_round),
                    "schedule_bohr": round_bond_schedule,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    # ---- Phase C: online learning (warm-start from Phase B if pretrained) -
    logger.info(
        "==== Phase C: online learning max_rounds=%s (warm_start=%s, pretrained=%s) ====",
        cfg.max_rounds,
        cfg.warm_start,
        bool(pretrain_meta.get("enabled")),
    )
    for round_i in range(1, cfg.max_rounds + 1):
        bonds_this_round = round_bond_schedule[round_i - 1] if round_bond_schedule else None
        dataset, log, all_converged, stop_early = run_validation_round(
            round_i=round_i,
            cfg=cfg,
            exp_yaml=exp_yaml,
            out=out,
            handle=handle,
            dataset=dataset,
            round_bonds_bohr=bonds_this_round,
        )
        round_logs.append(log)

        if stop_early:
            break

        if all_converged and cfg.stop_on_md_converged:
            # Staged tolerances: only early-stop when the *final* tol is active.
            final_tol = float(cfg.energy_tolerance_hartree)
            active_tol = float(cfg.resolve_round_tolerance(round_i))
            if abs(active_tol - final_tol) <= 1e-15 * max(1.0, final_tol):
                converged = True
                logger.info(
                    "All MD frames within final tolerance %.6g Ha — stopping early.",
                    final_tol,
                )
                break
            logger.info(
                "MD frames within stage tolerance %.6g Ha (final=%.6g); continuing.",
                active_tol,
                final_tol,
            )
            converged = False
        if all_converged and not cfg.stop_on_md_converged:
            logger.info(
                "MD frames within tolerance but stop_on_md_converged=False; "
                "continuing scheduled bond rounds."
            )
            converged = True

    # Final coverage after OL
    final_coverage = {"bound": 0, "dissociating": 0, "beyond_cutoff": 0, "unknown": 0}
    for fr in dataset.frames:
        bond = diatomic_bond_bohr(fr.positions_bohr)
        regime = classify_bond_regime(
            bond,
            dissociation_bond_bohr=cfg.dissociation_bond_bohr,
            cutoff_bohr=cutoff_b,
        )
        final_coverage[regime] = final_coverage.get(regime, 0) + 1
    dissociation_policy["final_coverage"] = final_coverage
    (out / "dissociation_cutoff_policy.json").write_text(
        json.dumps(dissociation_policy, indent=2),
        encoding="utf-8",
    )

    summary = build_md_validation_summary(
        experiment_yaml=exp_yaml,
        output_dir=out,
        config=cfg,
        n_total_frames=len(dataset.frames),
        round_logs=round_logs,
        converged=converged,
        species_list=list(handle.species_list),
        accuracy_threshold_hartree=accuracy_threshold_hartree,
    )
    summary["phases"] = {
        "A_quantum_bond_scan": {
            "n_seed_geometries": int(cfg.n_seed_geometries),
            "seed_mode": str(cfg.seed_mode),
            "seed_bond_min_bohr": float(cfg.seed_bond_min_bohr),
            "seed_bond_max_bohr": float(cfg.seed_bond_max_bohr),
        },
        "B_pretrain": pretrain_meta,
        "C_online_learning": {
            "max_rounds": int(cfg.max_rounds),
            "n_rounds_completed": len(round_logs),
            "warm_start": bool(cfg.warm_start),
        },
        "dissociation_cutoff_policy": dissociation_policy,
    }
    write_md_validation_summary(out, summary)
    # Also persist the final cumulative dataset for downstream reuse.
    export_extended_xyz(dataset, out / "train_final.xyz")
    return summary


# Backward-compatible private aliases (imported by examples/tests).
_make_seed_geometries = make_seed_geometries
_jitter_geometries = jitter_geometries
_bond_stretch_geometries = bond_stretch_geometries

__all__ = [
    "Ensemble",
    "MdValidationLoopConfig",
    "FrameValidationRecord",
    "MdValidationRoundLog",
    "run_md_validation_loop",
]

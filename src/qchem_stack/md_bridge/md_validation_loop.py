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

import logging
from pathlib import Path
from typing import Any

import numpy as np

from qchem_stack.md_bridge.exporter import export_extended_xyz
from qchem_stack.md_bridge.md_loop_config import (
    Ensemble,
    FrameValidationRecord,
    MdValidationLoopConfig,
    MdValidationRoundLog,
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
    cfg = config or MdValidationLoopConfig()
    exp_yaml = Path(experiment_yaml)
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

    # ---- Optional seed augmentation -------------------------------------
    if cfg.n_seed_geometries > 0:
        base_pos = np.asarray(dataset.frames[0].positions_bohr, dtype=np.float64)
        seed_geoms = make_seed_geometries(
            base_pos,
            n=cfg.n_seed_geometries,
            mode=cfg.seed_mode,
            sigma_bohr=cfg.seed_jitter_bohr,
            bond_min_bohr=cfg.seed_bond_min_bohr,
            bond_max_bohr=cfg.seed_bond_max_bohr,
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

    # ---- Build model -----------------------------------------------------
    handle = build_force_field_handle(
        species_list,
        backend=cfg.force_field_backend,
        preset=cfg.qmlff_preset,
        builder_overrides=cfg.qmlff_builder_overrides,
        qmp_h2_overrides=cfg.qmp_h2_overrides,
    )

    round_logs: list[MdValidationRoundLog] = []
    converged = False

    # ---- Active-learning rounds ------------------------------------------
    for round_i in range(1, cfg.max_rounds + 1):
        dataset, log, all_converged, stop_early = run_validation_round(
            round_i=round_i,
            cfg=cfg,
            exp_yaml=exp_yaml,
            out=out,
            handle=handle,
            dataset=dataset,
        )
        round_logs.append(log)

        if stop_early:
            break

        if all_converged:
            converged = True
            logger.info("All MD frames within tolerance — stopping loop early.")
            break

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

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
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import yaml

from qchem_stack.md_bridge.exporter import export_extended_xyz
from qchem_stack.md_bridge.qchem_labeler import (
    EnergyReference,
    LabelingResult,
    TheoryLevel,
    label_base_geometry_only,
    label_geometries_with_pipeline,
    merge_qmef_datasets,
)
from qchem_stack.md_bridge.qmlff_adapter import (
    JaxMdTrajectory,
    QmlffModelHandle,
    atomic_number_to_symbol,
    build_force_field_handle,
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

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config dataclass (independent of ExperimentConfig schema on purpose)
# ---------------------------------------------------------------------------


Ensemble = Literal["nve", "nvt_langevin", "nvt_nose_hoover"]
SeedMode = Literal["jitter", "bond_stretch"]
MdInitFrame = Literal["base", "last"]
ForceFieldBackend = Literal[
    "qmlff_preset",
    "qmlff_quantum",
    "qmlff_angle",
    "qmlff_qmp_h2",
    "classical_h2",
]


@dataclass
class MdValidationLoopConfig:
    """All knobs for :func:`run_md_validation_loop`.

    The loop deliberately keeps its own stdlib dataclass rather than extending
    :class:`~qchem_stack.config.ExperimentConfig`: this keeps the orchestration
    schema stable across qchem releases and avoids leaking ML/MD concerns into
    the chemistry config tree.

    Two-stage labeling parallels the existing
    :class:`qmlff.data.qchem_online_loop.TwoStageLabelingSpec`: every candidate
    is first scored with cheap ``hf_scf`` screening, then the top-k with the
    largest QML-vs-qchem energy gap are upgraded to ``full_pipeline``.

    Attributes:
        max_rounds: number of active-learning iterations after cold-start.
        qmlff_preset: QML-FF preset name (``atomic_amplitude`` etc.) when
            ``force_field_backend`` is ``qmlff_preset`` or ``qmlff_angle``.
        force_field_backend: ``qmlff_preset`` | ``qmlff_quantum`` | ``qmlff_angle``
            | ``qmlff_qmp_h2`` | ``classical_h2``.
        qmlff_builder_overrides: forwarded to the preset ``get_config(**overrides)``
        qmp_h2_overrides: forwarded to ``SchurSchemeBQMLFFConfig`` for QMP path.
        lr_scheduler: QML-FF ``TrainerConfig.lr_scheduler`` (use ``constant`` for AL).
        warm_start_params_only: reuse model params each round but reset optimizer.
        energy_normalization: ``subtract_mean`` | ``per_atom`` | ``none`` (QML-FF native).
        grad_clip: forwarded to ``TrainerConfig.grad_clip``.
        qmlff_species_list: ordered list of element symbols the model must
            cover for all geometries it will see; defaults to whatever is in
            the experiment YAML's base molecule.
        n_seed_geometries: extra seed geometries to label and add to the
            initial training set (set to 0 for a strict 0-data cold-start).
        seed_mode: ``jitter`` (Gaussian noise) or ``bond_stretch`` (scan the
            diatomic bond length; falls back to jitter for non-diatomics).
        seed_jitter_bohr: σ of the Gaussian jitter (Bohr) when ``seed_mode=jitter``.
        seed_bond_min_bohr / seed_bond_max_bohr: bond-length scan range (Bohr)
            when ``seed_mode=bond_stretch``.
        md_init_frame: ``base`` starts MD from the equilibrium/base geometry;
            ``last`` uses the most recently merged training frame.
        n_epochs_per_round / batch_size / learning_rate / force_weight:
            forwarded to :class:`qmlff.training.TrainerConfig` each round.
        warm_start: reuse optimizer state from the previous round.
        md_ensemble / md_n_steps / md_dt_fs / md_temperature_K / md_save_stride /
            md_seed / md_gamma_ps_inv / md_tau_fs: MD knobs (see
            :func:`run_jaxmd_trajectory`).
        n_candidate_frames: how many MD frames to sample for validation.
        energy_tolerance_hartree: per-frame |ΔE| convergence target.
        add_top_k_per_round: ≤ ``n_candidate_frames``; merge the K worst gaps
            back into the training dataset each round.
        label_energy_reference: ``variational`` / ``scf`` / ``pauli_protocol``
            for the **labeling step** (training labels).
        label_screening_theory_level: ``hf_scf`` (cheap) or ``full_pipeline``
            (slow) for the *full pool* screening pass.
        label_top_theory_level: ``full_pipeline`` (default) for the top-k
            geometries selected by the gap; ``hf_scf`` to stay HF throughout.
        dedupe_decimals: round positions (Bohr) to this many decimals when
            deduplicating frames during dataset merges.
        include_hf_nuclear_gradient: attach analytic HF forces (Hartree/Bohr)
            from PySCF where available (non-PBC only).
        write_per_round_extxyz: dump the cumulative dataset + MD trajectory
            for every round.
        seed: PRNG seed for seed-geometry jitter (and reproducibility).
        force_weight_during_screening: pass ``force_weight`` to the inner
            screening-only trainer when finer force fitting is required.
    """

    max_rounds: int = 2
    force_field_backend: ForceFieldBackend = "qmlff_preset"
    qmlff_preset: str = "atomic_amplitude"
    qmlff_builder_overrides: dict[str, Any] | None = None
    qmp_h2_overrides: dict[str, Any] | None = None
    qmlff_species_list: list[str] | None = None

    # Seeding (round 0 augmentation)
    n_seed_geometries: int = 0
    seed_mode: SeedMode = "jitter"
    seed_jitter_bohr: float = 0.08
    seed_bond_min_bohr: float = 0.8
    seed_bond_max_bohr: float = 2.2

    # QML-FF training
    n_epochs_per_round: int = 3
    batch_size: int = 1
    learning_rate: float = 1e-3
    force_weight: float = 100.0
    lr_scheduler: str = "constant"
    warm_start: bool = False
    warm_start_params_only: bool = True
    energy_normalization: str | None = "subtract_mean"
    grad_clip: float = 1.0
    qmlff_checkpoint_save_freq: int | None = 0
    """QML-FF ``TrainerConfig.save_freq``; ``0`` or ``None`` = only ``final`` checkpoint."""

    # JAX-MD
    md_ensemble: Ensemble = "nvt_langevin"
    md_n_steps: int = 100
    md_dt_fs: float = 0.5
    md_temperature_K: float = 300.0
    md_save_stride: int = 5
    md_seed: int = 0
    md_gamma_ps_inv: float = 0.1
    md_tau_fs: float = 100.0
    md_init_frame: MdInitFrame = "last"
    cutoff_ang: float | None = None
    max_neighbors: int = 32

    # Active learning
    n_candidate_frames: int = 4
    energy_tolerance_hartree: float = 5.0e-4  # ≈ 13.6 meV
    add_top_k_per_round: int = 2
    label_energy_reference: EnergyReference = "variational"
    label_screening_theory_level: TheoryLevel = "hf_scf"
    label_top_theory_level: TheoryLevel = "full_pipeline"
    include_hf_nuclear_gradient: bool = True
    dedupe_decimals: int = 4

    # IO
    write_per_round_extxyz: bool = True
    seed: int = 0

    @classmethod
    def from_yaml(cls, path: str | Path) -> MdValidationLoopConfig:
        """Load from a flat YAML mapping (only known fields are honored)."""
        p = Path(path)
        if not p.is_file():
            raise FileNotFoundError(f"MD validation loop YAML not found: {p}")
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if not isinstance(raw, dict):
            raise ValueError(f"YAML at {p} must be a mapping; got {type(raw).__name__}")
        # Filter to known fields so future YAMLs with extra keys don't crash.
        valid = set(cls.__dataclass_fields__.keys())
        clean = {k: v for k, v in raw.items() if k in valid}
        return cls(**clean)


# ---------------------------------------------------------------------------
# Per-round + summary records
# ---------------------------------------------------------------------------


@dataclass
class FrameValidationRecord:
    """Per-frame |ΔE| record used to decide which MD frames to re-label."""

    frame_index: int
    time_ps: float
    energy_qml_hartree: float
    energy_qchem_hartree: float
    delta_hartree: float
    abs_delta_hartree: float
    converged: bool
    theory_level: str


@dataclass
class MdValidationRoundLog:
    round_index: int
    n_train_before: int
    n_train_after: int
    n_md_frames_sampled: int
    max_abs_delta_hartree: float
    mean_abs_delta_hartree: float
    converged: bool
    training_metrics: dict[str, Any] = field(default_factory=dict)
    frames: list[FrameValidationRecord] = field(default_factory=list)
    failures: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------


def run_md_validation_loop(
    experiment_yaml: str | Path,
    *,
    config: MdValidationLoopConfig | None = None,
    output_dir: str | Path = "results/qmlff_md_validation",
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
        seed_geoms = _make_seed_geometries(
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
            trajectory, n_candidates=cfg.n_candidate_frames, skip_initial=True
        )
        if not candidate_geoms:
            logger.warning(
                "round %s: no MD frames available for validation (n_steps=%s, save_stride=%s);"
                " stopping loop",
                round_i,
                cfg.md_n_steps,
                cfg.md_save_stride,
            )
            round_logs.append(
                MdValidationRoundLog(
                    round_index=round_i,
                    n_train_before=n_before,
                    n_train_after=n_before,
                    n_md_frames_sampled=0,
                    max_abs_delta_hartree=float("nan"),
                    mean_abs_delta_hartree=float("nan"),
                    converged=False,
                    training_metrics=dict(handle.train_meta),
                )
            )
            break

        # Re-label every candidate via cheap HF screening first.
        screen_result: LabelingResult = label_geometries_with_pipeline(
            exp_yaml,
            extra_coordinates_bohr=candidate_geoms,
            energy_reference="scf"
            if cfg.label_screening_theory_level == "hf_scf"
            else cfg.label_energy_reference,
            theory_level=cfg.label_screening_theory_level,
            include_hf_nuclear_gradient=cfg.include_hf_nuclear_gradient,
            failure_isolation=True,
        )

        # Per-frame delta vs QML-FF.
        records, by_index = _build_frame_records(
            handle=handle,
            candidate_geoms=candidate_geoms,
            atomic_numbers=init_zs,
            screen_result=screen_result,
            tolerance_hartree=cfg.energy_tolerance_hartree,
            label_theory_level=cfg.label_screening_theory_level,
            trajectory=trajectory,
        )

        # If all converged → stop.
        max_abs = max((r.abs_delta_hartree for r in records), default=float("nan"))
        mean_abs = (
            float(np.mean([r.abs_delta_hartree for r in records])) if records else float("nan")
        )
        all_converged = bool(records) and all(r.converged for r in records)

        # Choose top-K geometries to upgrade to the higher-fidelity label
        # (or just use the screening labels when label_top_theory_level matches).
        upgrade_records = sorted(records, key=lambda r: r.abs_delta_hartree, reverse=True)[
            : max(0, int(cfg.add_top_k_per_round))
        ]
        upgrade_geoms = [candidate_geoms[r.frame_index] for r in upgrade_records]

        upgrade_dataset: QMEFDataset = QMEFDataset(frames=[])
        if upgrade_geoms:
            if cfg.label_top_theory_level == cfg.label_screening_theory_level:
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
            dataset = merge_qmef_datasets(
                dataset, upgrade_dataset, dedupe_decimals=cfg.dedupe_decimals
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
        round_logs.append(log)

        if cfg.write_per_round_extxyz:
            export_extended_xyz(dataset, out / f"train_round_{round_i}.xyz")
        _write_round_metrics(out, round_i, log, by_index)

        logger.info(
            "round %s: n_train %s → %s | max|ΔE|=%.6f Ha | mean|ΔE|=%.6f Ha | converged=%s",
            round_i,
            n_before,
            n_after,
            max_abs,
            mean_abs,
            all_converged,
        )

        if all_converged:
            converged = True
            logger.info("All MD frames within tolerance — stopping loop early.")
            break

    summary = {
        "experiment_yaml": str(exp_yaml.resolve()),
        "output_dir": str(out.resolve()),
        "config": asdict(cfg),
        "n_total_frames": len(dataset.frames),
        "rounds": [_round_log_to_jsonable(log) for log in round_logs],
        "converged": bool(converged),
        "species_list": list(handle.species_list),
        "force_field_backend": cfg.force_field_backend,
        "qmlff_preset": cfg.qmlff_preset,
    }
    (out / "md_validation_summary.json").write_text(
        json.dumps(summary, indent=2, default=_json_default),
        encoding="utf-8",
    )
    # Also persist the final cumulative dataset for downstream reuse.
    export_extended_xyz(dataset, out / "train_final.xyz")
    return summary


# ---------------------------------------------------------------------------
# Helpers (private)
# ---------------------------------------------------------------------------


def _make_seed_geometries(
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
        stretched = _bond_stretch_geometries(
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
    return _jitter_geometries(base_bohr, n=n, sigma_bohr=sigma_bohr, rng=rng)


def _jitter_geometries(
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


def _bond_stretch_geometries(
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


def _build_frame_records(
    *,
    handle: QmlffModelHandle,
    candidate_geoms: list[list[list[float]]],
    atomic_numbers: Sequence[int],
    screen_result: LabelingResult,
    tolerance_hartree: float,
    label_theory_level: str,
    trajectory: JaxMdTrajectory,
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
    time_lookup = _trajectory_time_lookup(trajectory)

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
            delta = e_qml - e_ref
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


def _trajectory_time_lookup(trajectory: JaxMdTrajectory):
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


def _write_round_metrics(
    out: Path, round_i: int, log: MdValidationRoundLog, debug_by_idx: dict[int, dict[str, Any]]
) -> None:
    payload = {
        "round": _round_log_to_jsonable(log),
        "frames_debug": {str(k): v for k, v in debug_by_idx.items()},
    }
    (out / f"validation_round_{round_i}.json").write_text(
        json.dumps(payload, indent=2, default=_json_default),
        encoding="utf-8",
    )


def _round_log_to_jsonable(log: MdValidationRoundLog) -> dict[str, Any]:
    d = asdict(log)
    d["frames"] = [asdict(fr) for fr in log.frames]
    return d


def _json_default(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return float(obj)
    if hasattr(obj, "item"):
        return obj.item()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


__all__ = [
    "Ensemble",
    "MdValidationLoopConfig",
    "FrameValidationRecord",
    "MdValidationRoundLog",
    "run_md_validation_loop",
]

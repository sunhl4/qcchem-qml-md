"""Label arbitrary Bohr-coordinate geometries via ``run_pipeline_sync``.

This is a thin convenience over the existing
:func:`qchem_stack.md_bridge.from_pipeline.build_qmef_ml_attachment_repro_block`
flow that:

* loads (or accepts) an :class:`~qchem_stack.config.ExperimentConfig`,
* injects a list of extra geometries via ``md_ml_export.trajectory.extra_coordinates_bohr``,
* runs the in-process pipeline once,
* lifts ``out["repro"]["qmef_ml_attachment_v1"]["dataset"]`` back into a
  :class:`~qchem_stack.md_bridge.schema.QMEFDataset`.

It also offers a **failure-isolation** path: when batch labeling fails (e.g. one
geometry blows up the pipeline), it retries one geometry at a time and returns
whatever frames succeeded together with a structured list of failures.

This module is additive and does not alter the rest of ``md_bridge``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from qchem_stack.exceptions import PipelineError
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame

if TYPE_CHECKING:
    from collections.abc import Sequence

    from qchem_stack.config import ExperimentConfig

logger = logging.getLogger(__name__)


EnergyReference = Literal["variational", "scf", "pauli_protocol"]
TheoryLevel = Literal["hf_scf", "full_pipeline"]


# ---------------------------------------------------------------------------
# Result containers
# ---------------------------------------------------------------------------


@dataclass
class LabelingFailure:
    """One geometry that failed pipeline labeling (returned by failure-isolation path)."""

    index: int
    """0-based index into the ``extra_coordinates_bohr`` argument."""
    coordinates_bohr: list[list[float]]
    """The offending geometry (so callers can replay / log)."""
    error: str
    """``str(exc)`` for the most recent failure on that geometry."""


@dataclass
class LabelingResult:
    """Output of :func:`label_geometries_with_pipeline`.

    Attributes:
        dataset: a :class:`QMEFDataset` containing the **base geometry** as
            frame ``0`` and every successfully labeled extra geometry as
            subsequent frames.
        failures: per-geometry failures (empty when batch path succeeds).
        epistemic_bound: copy of ``repro.qmef_ml_attachment_v1.epistemic_bound``
            from the underlying pipeline run, when available.
        primary_repro_config_sha256_prefix: pipeline ``repro.config_sha256_prefix``.
    """

    dataset: QMEFDataset
    failures: list[LabelingFailure] = field(default_factory=list)
    epistemic_bound: str = ""
    primary_repro_config_sha256_prefix: str = ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def label_base_geometry_only(
    experiment_yaml: str | Path,
    *,
    energy_reference: EnergyReference = "variational",
    include_hf_nuclear_gradient: bool = True,
) -> LabelingResult:
    """Run the pipeline on the YAML's base geometry only; return a 1-frame dataset.

    Cheap entry point for "cold-start" mode of the MD-validation loop.
    """
    return label_geometries_with_pipeline(
        experiment_yaml,
        extra_coordinates_bohr=[],
        energy_reference=energy_reference,
        theory_level="hf_scf",
        include_hf_nuclear_gradient=include_hf_nuclear_gradient,
        failure_isolation=False,
    )


def label_geometries_with_pipeline(
    experiment_yaml: str | Path,
    extra_coordinates_bohr: Sequence[Sequence[Sequence[float]]],
    *,
    energy_reference: EnergyReference = "variational",
    theory_level: TheoryLevel = "hf_scf",
    include_hf_nuclear_gradient: bool = True,
    failure_isolation: bool = True,
) -> LabelingResult:
    """Label a base + extra-geometries batch using ``run_pipeline_sync``.

    Args:
        experiment_yaml: path to the qchem-stack experiment YAML defining the
            molecule, basis, SCF/quantum/active-space settings. The YAML is
            **not mutated on disk**; we work on a deep copy of the loaded
            :class:`ExperimentConfig`.
        extra_coordinates_bohr: list of ``(N, 3)`` geometries (Bohr) to label
            **in addition to** the base geometry already in the YAML. May be
            empty — then only the base frame is returned.
        energy_reference: primary-frame energy source. ``pauli_protocol`` and
            ``variational`` require ``quantum.pauli.use_protocol: true`` /
            a completed variational stage respectively (default).
        theory_level: ``hf_scf`` runs a fresh PySCF mean-field per geometry
            (fast); ``full_pipeline`` nests :func:`run_pipeline_sync` per
            geometry (slow but high-fidelity, including quantum stages).
        include_hf_nuclear_gradient: attach analytic HF nuclear forces
            (Hartree/Bohr) when PySCF gradient is available (non-PBC only).
        failure_isolation: if true and the batch run raises, fall back to
            per-geometry labeling and collect partial successes / failures.

    Returns:
        :class:`LabelingResult` with at least the base frame on success.

    Raises:
        :class:`qchem_stack.exceptions.PipelineError`: when the base pipeline
            itself fails or its output is missing ``repro.qmef_ml_attachment_v1``.
        :class:`FileNotFoundError`: when ``experiment_yaml`` is missing.
    """
    cfg_path = Path(experiment_yaml)
    if not cfg_path.is_file():
        raise FileNotFoundError(f"experiment_yaml not found: {cfg_path}")

    from qchem_stack.config import load_experiment_config

    base_cfg = load_experiment_config(cfg_path)

    extras = [[[float(x) for x in row] for row in geom] for geom in (extra_coordinates_bohr or [])]

    try:
        return _run_with_extras(
            base_cfg,
            cfg_path=cfg_path,
            extras=extras,
            energy_reference=energy_reference,
            theory_level=theory_level,
            include_hf_nuclear_gradient=include_hf_nuclear_gradient,
        )
    except Exception as exc:
        if not failure_isolation or not extras:
            raise
        logger.warning("batch labeling failed (%s); falling back to per-geometry isolation", exc)

    # Per-geometry fallback:
    # 1) try base-only first (must succeed; otherwise nothing to return)
    base_only = _run_with_extras(
        base_cfg,
        cfg_path=cfg_path,
        extras=[],
        energy_reference=energy_reference,
        theory_level=theory_level,
        include_hf_nuclear_gradient=include_hf_nuclear_gradient,
    )

    frames: list[QMFrame] = list(base_only.dataset.frames)
    failures: list[LabelingFailure] = []
    epistemic = base_only.epistemic_bound
    cfg_sha = base_only.primary_repro_config_sha256_prefix

    for i, geom in enumerate(extras):
        try:
            one = _run_with_extras(
                base_cfg,
                cfg_path=cfg_path,
                extras=[geom],
                energy_reference=energy_reference,
                theory_level=theory_level,
                include_hf_nuclear_gradient=include_hf_nuclear_gradient,
            )
        except Exception as exc:  # noqa: BLE001 - we record the message verbatim
            logger.warning("per-geometry labeling failed for index %s: %s", i, exc)
            failures.append(LabelingFailure(index=i, coordinates_bohr=geom, error=str(exc)))
            continue
        if len(one.dataset.frames) >= 2:
            frames.append(one.dataset.frames[1])
        else:
            failures.append(
                LabelingFailure(
                    index=i,
                    coordinates_bohr=geom,
                    error="pipeline returned no extra frame for this geometry",
                )
            )

    return LabelingResult(
        dataset=QMEFDataset(
            frames=frames,
            provenance_yaml=base_only.dataset.provenance_yaml,
        ),
        failures=failures,
        epistemic_bound=epistemic,
        primary_repro_config_sha256_prefix=cfg_sha,
    )


def merge_qmef_datasets(
    *datasets: QMEFDataset,
    dedupe_decimals: int | None = 4,
) -> QMEFDataset:
    """Concatenate one or more :class:`QMEFDataset` instances, optionally dedup by geometry.

    Two frames are considered duplicates when:
      * ``atomic_numbers`` match exactly, and
      * positions agree to ``dedupe_decimals`` significant decimals in **Bohr**.

    Keeps the first occurrence; provenance YAML is concatenated.
    """
    if not datasets:
        return QMEFDataset(frames=[])
    if len(datasets) == 1 and dedupe_decimals is None:
        return datasets[0]

    seen: set[tuple[Any, ...]] = set()
    out_frames: list[QMFrame] = []
    out_prov: list[str] = []

    for ds in datasets:
        if not ds.frames:
            if ds.provenance_yaml:
                out_prov.append(ds.provenance_yaml)
            continue
        for fr in ds.frames:
            key: tuple[Any, ...]
            if dedupe_decimals is None:
                key = (id(fr),)
            else:
                pos = tuple(
                    tuple(round(float(x), int(dedupe_decimals)) for x in row)
                    for row in fr.positions_bohr
                )
                key = (tuple(int(z) for z in fr.atomic_numbers), pos)
            if key in seen:
                continue
            seen.add(key)
            out_frames.append(fr)
        if ds.provenance_yaml:
            out_prov.append(ds.provenance_yaml)

    return QMEFDataset(frames=out_frames, provenance_yaml="\n---\n".join(out_prov))


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _run_with_extras(
    base_cfg: ExperimentConfig,
    *,
    cfg_path: Path,
    extras: list[list[list[float]]],
    energy_reference: EnergyReference,
    theory_level: TheoryLevel,
    include_hf_nuclear_gradient: bool,
) -> LabelingResult:
    """One shot at the pipeline. Caller wraps for failure isolation."""
    from qchem_stack.config import MdMlExportSpec
    from qchem_stack.config.md_ml_export import MdMlTrajectorySpec
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg = base_cfg.model_copy(
        deep=True,
        update={
            "md_ml_export": MdMlExportSpec(
                attach_single_frame_to_repro=True,
                energy_reference=energy_reference,
                include_hf_nuclear_gradient=bool(include_hf_nuclear_gradient),
                trajectory=MdMlTrajectorySpec(
                    extra_coordinates_bohr=extras,
                    theory_level=theory_level,
                ),
            ),
        },
    )

    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    if not isinstance(out, dict):
        raise PipelineError(f"run_pipeline_sync returned unexpected type {type(out).__name__}")
    repro = out.get("repro")
    if not isinstance(repro, dict):
        raise PipelineError("pipeline output missing 'repro' block")
    block = repro.get("qmef_ml_attachment_v1")
    if not isinstance(block, dict):
        raise PipelineError(
            "pipeline output missing repro.qmef_ml_attachment_v1; "
            "the labeler enables md_ml_export.attach_single_frame_to_repro itself, "
            "so a missing block points to a deeper pipeline failure"
        )
    raw = block.get("dataset")
    if not isinstance(raw, dict):
        raise PipelineError(
            "qmef_ml_attachment_v1.dataset is not a dict; cannot reconstruct QMEFDataset"
        )
    dataset = QMEFDataset.model_validate(raw)
    return LabelingResult(
        dataset=dataset,
        failures=[],
        epistemic_bound=str(block.get("epistemic_bound") or ""),
        primary_repro_config_sha256_prefix=str(repro.get("config_sha256_prefix") or ""),
    )


__all__ = [
    "EnergyReference",
    "TheoryLevel",
    "LabelingFailure",
    "LabelingResult",
    "label_base_geometry_only",
    "label_geometries_with_pipeline",
    "merge_qmef_datasets",
]

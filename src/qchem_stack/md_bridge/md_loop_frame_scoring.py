"""Frame scoring / upgrade-selection helpers for the MD validation loop.

Pure helpers extracted from :mod:`qchem_stack.md_bridge.md_loop_rounds` so the
single-round orchestrator stays under the code-health line cap. These compute
per-frame |ΔE| records, the constant energy-offset calibration, the
trajectory time lookup, and the top-K worst-frame upgrade selection — no
orchestration or I/O side effects beyond labeling calls.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.md_bridge.md_loop_config import (
    FrameValidationRecord,
    MdValidationLoopConfig,
)
from qchem_stack.md_bridge.md_loop_geometry import (
    classify_bond_regime,
    diatomic_bond_bohr,
    resolve_cutoff_bohr,
    resolve_max_train_bond_bohr,
)
from qchem_stack.md_bridge.qchem_labeler import (
    EnergyReference,
    LabelingResult,
    TheoryLevel,
    label_geometries_with_pipeline,
)
from qchem_stack.md_bridge.qmlff_adapter import (
    JaxMdTrajectory,
    QmlffModelHandle,
    predict_energy_forces_hartree,
    qmlff_handle_to_qmef_frame,
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

    Frames with bond length beyond ``max_train_bond_bohr`` (default ≈ 0.95 ×
    FF cutoff) are skipped: past the cutoff the model does not evaluate the
    pair interaction, so MD-blown geometries must not pollute training.
    Dissociating-but-within-cutoff geometries are kept for asymptote coverage.
    """
    cutoff_b = resolve_cutoff_bohr(cfg.cutoff_ang)
    max_bond = resolve_max_train_bond_bohr(
        max_train_bond_bohr=cfg.max_train_bond_bohr,
        cutoff_ang=cfg.cutoff_ang,
    )
    ranked = sorted(records, key=lambda r: r.abs_delta_hartree, reverse=True)
    upgrade_records: list[FrameValidationRecord] = []
    skipped: list[dict[str, Any]] = []
    for rec in ranked:
        if len(upgrade_records) >= max(0, int(cfg.add_top_k_per_round)):
            break
        geom = candidate_geoms[rec.frame_index]
        bond = diatomic_bond_bohr(geom)
        regime = classify_bond_regime(
            bond,
            dissociation_bond_bohr=cfg.dissociation_bond_bohr,
            cutoff_bohr=cutoff_b,
        )
        if bond is not None and bond > max_bond:
            skipped.append(
                {
                    "frame_index": rec.frame_index,
                    "bond_bohr": bond,
                    "regime": regime,
                    "reason": "bond_exceeds_max_train_or_cutoff",
                    "max_train_bond_bohr": max_bond,
                    "cutoff_bohr": cutoff_b,
                }
            )
            continue
        upgrade_records.append(rec)

    if skipped:
        logger.info(
            "skipped %s MD candidate(s) for train merge (beyond cutoff/max train bond): %s",
            len(skipped),
            [
                {
                    "i": s["frame_index"],
                    "R": round(float(s["bond_bohr"]), 3),
                    "regime": s["regime"],
                }
                for s in skipped
            ],
        )

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

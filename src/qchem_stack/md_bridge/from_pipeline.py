"""Build :class:`QMEFDataset` snapshots from :func:`~qchem_stack.orchestration.pipeline.run_pipeline_sync` results."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

import yaml

from qchem_stack.contracts.schema_ids import QMEF_ML_ATTACHMENT_V1
from qchem_stack.md_bridge.from_pipeline_extract import (
    active_space_digest,
    as_pyscf_rhf,
    atomic_numbers_from_pyscf_mol,
    config_sha_prefix,
    energy_hartree_from_pipeline_out,
    hf_nuclear_forces_neg_gradient_hartree_bohr,
    normalize_coords,
    primary_qmframe,
    protocol_hash_prefix,
    rhf_at_coordinates,
)
from qchem_stack.md_bridge.from_pipeline_types import (
    PipelineOut,
    QmefAttachmentContext,
    QmefDatasetPayload,
    QmefFrameMeta,
    QmefFramePayload,
    QmefMlAttachmentReproBlock,
)
from qchem_stack.md_bridge.pipeline_runner import PipelineRunner, resolve_pipeline_runner
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def _extra_frame_hf_scf(
    cfg: ExperimentConfig,
    out: PipelineOut,
    coords: list[list[float]],
    *,
    index: int,
) -> QMFrame:
    from qchem_stack.md_bridge.from_pipeline_extract import qmframe_from_rhf

    rhf = rhf_at_coordinates(cfg, coords)
    tag = f"{cfg.scf.method}/HF-SCF-trajectory[{index}]"
    return qmframe_from_rhf(
        cfg,
        out,
        rhf,
        coords,
        energy_hartree=float(rhf.e_tot),
        method_tag=tag,
    )


def _extra_frame_full_pipeline(
    cfg: ExperimentConfig,
    primary_out: PipelineOut,
    coords: list[list[float]],
    *,
    index: int,
    cfg_path: Path | None,
    pipeline_runner: PipelineRunner | None = None,
) -> QMFrame:
    from qchem_stack.config import MdMlExportSpec

    child = cfg.model_copy(
        deep=True,
        update={
            "molecule": cfg.molecule.model_copy(
                update={"coordinates": normalize_coords(coords), "coordinate_unit": "bohr"}
            ),
            "md_ml_export": MdMlExportSpec(),
        },
    )
    runner = resolve_pipeline_runner(pipeline_runner)
    out_c = runner(child, cfg_path=cfg_path)
    energy = energy_hartree_from_pipeline_out(cfg, out_c)
    rhf_g = rhf_at_coordinates(cfg, coords)
    forces: list[list[float]] = []
    if cfg.md_ml_export.include_hf_nuclear_gradient:
        frc = hf_nuclear_forces_neg_gradient_hartree_bohr(rhf_g, str(cfg.scf.method))
        if frc is not None:
            forces = frc
    zs = atomic_numbers_from_pyscf_mol(rhf_g)
    tag = f"{cfg.scf.method}/{cfg.quantum.algorithm}/JW-{cfg.active_space.mapping.fermion_qubit}/trajectory-FP[{index}]"
    return QMFrame(
        atomic_numbers=zs,
        positions_bohr=normalize_coords(coords),
        energy_hartree=float(energy),
        forces_hartree_bohr=forces,
        charge=int(cfg.molecule.charge),
        multiplicity=int(cfg.molecule.multiplicity),
        box=None,
        method_tag=tag,
        active_space_hash=active_space_digest(cfg),
        protocol_hash=protocol_hash_prefix(primary_out),
        repro_config_sha256_prefix=config_sha_prefix(primary_out),
        backend_noise_tag=str(cfg.backend.provider),
    )


def build_qmef_ml_attachment_repro_block(
    cfg: ExperimentConfig,
    out: PipelineOut,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
    pipeline_runner: PipelineRunner | None = None,
) -> QmefMlAttachmentReproBlock:
    """
    Canonical ``repro.qmef_ml_attachment_v1`` — one **primary** frame from the finished pipeline plus optional
    **extra** geometries (HF-SCF-only or full nested pipelines per ``md_ml_export.trajectory_theory_level``).
    """
    spec = cfg.md_ml_export
    rhf = as_pyscf_rhf(reference)
    frames: list[QMFrame] = [primary_qmframe(cfg, out, rhf)]
    frame_meta: list[QmefFrameMeta] = [
        {
            "index": 0,
            "coordinates_source": "molecule.coordinates_bohr",
            "energy_theory": "primary_pipeline",
            "energy_reference_mode": spec.energy_reference,
            "forces_theory": "hf_rhf_analytic_same_reference_geometry"
            if spec.include_hf_nuclear_gradient
            else "none",
        }
    ]

    for i, raw_coords in enumerate(spec.trajectory.extra_coordinates_bohr):
        coords = normalize_coords(raw_coords)
        idx = i + 1
        if spec.trajectory.theory_level == "full_pipeline":
            frames.append(
                _extra_frame_full_pipeline(
                    cfg,
                    out,
                    coords,
                    index=i,
                    cfg_path=cfg_path,
                    pipeline_runner=pipeline_runner,
                )
            )
            fm_energy = "nested_full_pipeline"
        else:
            frames.append(_extra_frame_hf_scf(cfg, out, coords, index=i))
            fm_energy = "hf_scf_only"
        frame_meta.append(
            {
                "index": idx,
                "coordinates_source": f"md_ml_export.extra_coordinates_bohr[{i}]",
                "energy_theory": fm_energy,
                "energy_reference_mode": spec.energy_reference
                if fm_energy == "nested_full_pipeline"
                else "scf_total",
                "forces_theory": (
                    "hf_rhf_analytic_same_geometry" if spec.include_hf_nuclear_gradient else "none"
                ),
            }
        )

    prov = yaml.safe_dump(
        {
            "experiment_id": cfg.experiment_id,
            "md_ml_export": spec.model_dump(mode="json"),
            "n_frames": len(frames),
            "frame_meta": frame_meta,
        },
        sort_keys=False,
        allow_unicode=True,
    )
    ds = QMEFDataset(frames=frames, provenance_yaml=prov)

    epistemic = (
        "QMEF attachment: frame 0 uses the primary pipeline geometry; "
        f"energy for frame 0 follows md_ml_export.energy_reference ({spec.energy_reference}: variational | scf | pauli_protocol). "
        "Pauli energy requires quantum.pauli.use_protocol and a completed Pauli stage. "
        "Extra frames use md_ml_export.extra_coordinates_bohr; trajectory_theory_level hf_scf runs PySCF mean-field only "
        "per geometry; full_pipeline re-invokes run_pipeline_sync per geometry (cost scales linearly; nested jobs do not attach QMEF). "
        "When include_hf_nuclear_gradient is true, forces are analytic HF −∂E/∂R (Hartree/Bohr) at that geometry's RHF reference "
        "(including after nested full_pipeline energies); non-PBC only; failures yield empty forces."
    )

    return {
        "schema": QMEF_ML_ATTACHMENT_V1,
        "epistemic_bound": epistemic,
        "frame_meta": frame_meta,
        "dataset": cast("QmefDatasetPayload", ds.model_dump(mode="json")),
    }


def build_qmef_ml_attachment_from_context(
    ctx: QmefAttachmentContext,
    reference: ClassicalMeanFieldReference,
    *,
    pipeline_runner: PipelineRunner | None = None,
) -> QmefMlAttachmentReproBlock:
    """Build QMEF attachment from a :class:`QmefAttachmentContext`."""
    return build_qmef_ml_attachment_repro_block(
        ctx.cfg,
        ctx.out,
        reference,
        cfg_path=ctx.cfg_path,
        pipeline_runner=pipeline_runner,
    )


def build_qmef_dataset_single_frame_repro_block(
    cfg: ExperimentConfig,
    out: PipelineOut,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
    pipeline_runner: PipelineRunner | None = None,
) -> QmefMlAttachmentReproBlock:
    """Backward-compatible name — delegates to :func:`build_qmef_ml_attachment_repro_block`."""
    return build_qmef_ml_attachment_repro_block(
        cfg,
        out,
        reference,
        cfg_path=cfg_path,
        pipeline_runner=pipeline_runner,
    )


__all__ = [
    "PipelineOut",
    "QmefAttachmentContext",
    "QmefDatasetPayload",
    "QmefFrameMeta",
    "QmefFramePayload",
    "QmefMlAttachmentReproBlock",
    "build_qmef_dataset_single_frame_repro_block",
    "build_qmef_ml_attachment_from_context",
    "build_qmef_ml_attachment_repro_block",
]

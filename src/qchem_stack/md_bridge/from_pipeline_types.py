"""Typed ingress shapes for QMEF attachment from pipeline results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypedDict

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.config import ExperimentConfig

# PipelineResultV1-shaped dict from run_pipeline_sync / run_pipeline_from_config.
PipelineOut = dict[str, Any]


class QmefFramePayload(TypedDict, total=False):
    atomic_numbers: list[int]
    positions_bohr: list[list[float]]
    energy_hartree: float
    forces_hartree_bohr: list[list[float]]
    charge: int
    multiplicity: int
    box: list[float] | None
    method_tag: str
    active_space_hash: str
    protocol_hash: str
    repro_config_sha256_prefix: str
    backend_noise_tag: str


class QmefDatasetPayload(TypedDict):
    frames: list[QmefFramePayload]
    provenance_yaml: str


class QmefFrameMeta(TypedDict):
    index: int
    coordinates_source: str
    energy_theory: str
    energy_reference_mode: str
    forces_theory: str


class QmefMlAttachmentReproBlock(TypedDict):
    schema: str
    epistemic_bound: str
    frame_meta: list[QmefFrameMeta]
    dataset: QmefDatasetPayload


@dataclass(frozen=True)
class QmefAttachmentContext:
    """Typed ingress for QMEF attachment from a completed pipeline row."""

    cfg: ExperimentConfig
    out: PipelineOut
    cfg_path: Path | None = None


__all__ = [
    "PipelineOut",
    "QmefAttachmentContext",
    "QmefDatasetPayload",
    "QmefFrameMeta",
    "QmefFramePayload",
    "QmefMlAttachmentReproBlock",
]

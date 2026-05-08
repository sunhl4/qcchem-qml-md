from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field


class QMFrame(BaseModel):
    atomic_numbers: list[int]
    positions_bohr: list[list[float]]
    energy_hartree: float
    forces_hartree_bohr: list[list[float]] = Field(default_factory=list)
    charge: int = 0
    multiplicity: int = 1
    box: list[float] | None = None
    method_tag: str = ""
    active_space_hash: str = ""
    protocol_hash: str = Field(
        default="",
        description="Protocol or job digest when the frame is tied to a pipeline run.",
    )
    repro_config_sha256_prefix: str = Field(
        default="",
        description="Optional: repro config_sha256_prefix from the same experiment run as this frame.",
    )
    backend_noise_tag: str = ""


class QMEFDataset(BaseModel):
    """Quantum / classical energies + forces for MLIP training."""

    frames: list[QMFrame]
    provenance_yaml: str = ""

    def model_dump_np(self) -> dict[str, Any]:
        return self.model_dump()


@dataclass
class DatasetBundle:
    pydantic: QMEFDataset

"""MD/ML attachment controls for exporting QMEF-compatible repro snapshots."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_FORBID = ConfigDict(extra="forbid")


class MdMlTrajectorySpec(BaseModel):
    model_config = _FORBID

    extra_coordinates_bohr: list[list[list[float]]] = Field(
        default_factory=list,
        description="Extra geometries (n_atom x 3 Bohr each).",
    )
    theory_level: Literal["hf_scf", "full_pipeline"] = Field(
        default="hf_scf",
        description="How extra geometries are evaluated.",
    )


class MdMlExportSpec(BaseModel):
    """Optional snapshot of md_bridge training schema onto repro."""

    model_config = _FORBID

    attach_single_frame_to_repro: bool = Field(
        default=False,
        description="Attach qmef_ml_attachment_v1 after pipeline completes.",
    )
    energy_reference: Literal["variational", "scf", "pauli_protocol"] = Field(
        default="variational",
        description="Primary-frame energy source for attachment.",
    )
    include_hf_nuclear_gradient: bool = Field(
        default=False,
        description="Attach analytic HF nuclear gradient when available.",
    )
    trajectory: MdMlTrajectorySpec = Field(default_factory=MdMlTrajectorySpec)

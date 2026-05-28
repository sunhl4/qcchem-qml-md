"""Nested SCF sub-schemas."""

from __future__ import annotations

from pydantic import Field

from ._base import ForbidExtraBase


class ScfDriverControlsSpec(ForbidExtraBase):
    """Driver-specific mean-field convergence controls (PySCF / Psi4)."""

    max_cycle: int | None = Field(default=None, ge=1, le=512, description="mf.max_cycle override.")
    chkfile: str | None = Field(default=None, description="Checkpoint path when supported.")
    init_guess: str | None = Field(default=None, description="Initial guess token when supported.")
    level_shift: float | None = Field(
        default=None, description="Mean-field level_shift when supported."
    )
    use_newton: bool = Field(
        default=False, description="Use Newton SCF for RHF/ROHF when available."
    )
    diis_space_dimension: int | None = Field(default=None, ge=2, description="DIIS space override.")
    density_fit: bool = Field(default=False, description="Enable density-fitting SCF.")
    density_fit_auxbasis: str | None = Field(
        default=None, description="Auxiliary basis for density fitting."
    )


ScfPyscfSpec = ScfDriverControlsSpec
ScfPsi4Spec = ScfDriverControlsSpec


class ScfPrecomputedSpec(ForbidExtraBase):
    bundle_path: str | None = Field(
        default=None,
        description="classical_reference_bundle_v1 JSON when driver=precomputed.",
    )

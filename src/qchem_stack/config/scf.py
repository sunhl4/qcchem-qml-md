"""SCF driver selection and mean-field convergence controls.

Field reference: ``docs/说明_scf配置.md``.
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, field_validator, model_validator

from ._base import ForbidExtraBase
from ._scf_validation import (
    validate_density_fit_auxbasis_consistency,
    validate_precomputed_bundle_requirements,
)
from .scf_enums import ScfDriverId
from .scf_specs import ScfPrecomputedSpec, ScfPsi4Spec, ScfPyscfSpec


class SCFSpec(ForbidExtraBase):
    """Classical Hartree–Fock driver selection (Hamiltonian build path is PySCF-first today)."""

    driver: str = Field(
        default=ScfDriverId.PYSCF.value,
        description="Classical backend id (pyscf, psi4, precomputed, or registered plugin).",
    )
    method: Literal["RHF", "ROHF", "UHF"] = Field(default="RHF", description="SCF spin treatment.")
    pyscf: ScfPyscfSpec = Field(default_factory=ScfPyscfSpec)
    psi4: ScfPsi4Spec = Field(default_factory=ScfPsi4Spec)
    precomputed: ScfPrecomputedSpec = Field(default_factory=ScfPrecomputedSpec)

    @field_validator("driver", mode="before")
    @classmethod
    def _coerce_driver(cls, v: object) -> str:
        if isinstance(v, ScfDriverId):
            return v.value
        key = str(v).strip().lower()
        if not key:
            raise ValueError("scf.driver must be a non-empty solver id.")
        if any(ch.isspace() for ch in key):
            raise ValueError(f"scf.driver must not contain whitespace: {v!r}.")
        return key

    @model_validator(mode="after")
    def _density_fit_auxbasis_consistency(self) -> SCFSpec:
        validate_density_fit_auxbasis_consistency(self)
        return self

    @model_validator(mode="after")
    def _precomputed_bundle_requirements(self) -> SCFSpec:
        validate_precomputed_bundle_requirements(self)
        return self

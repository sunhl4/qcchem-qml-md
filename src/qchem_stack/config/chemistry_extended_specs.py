"""Nested chemistry_extended sub-schemas."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from ._base import ForbidExtraBase


class ChemistrySolventSpec(ForbidExtraBase):
    model: Literal["none", "ddcosmo"] = Field(default="none", description="Solvent model for SCF.")
    epsilon: float = Field(default=78.3553, description="Dielectric constant for ddCOSMO.")


class ChemistryPbcSpec(ForbidExtraBase):
    cell_vectors_bohr: list[list[float]] | None = Field(
        default=None,
        description="3x3 lattice rows in Bohr for PySCF PBC.",
    )
    kpoint_mesh: list[int] = Field(
        default_factory=lambda: [1, 1, 1],
        description="Monkhorst-Pack mesh [nx, ny, nz].",
    )
    active_space_kpoint_index: int = Field(
        default=0,
        ge=0,
        description="KRHF MO index for active-space integrals.",
    )


class ChemistryAvasSpec(ForbidExtraBase):
    ao_labels: list[str] = Field(
        default_factory=list, description="AVAS atomic-orbital label strings."
    )
    threshold: float = Field(default=0.2, gt=0.0, le=1.0, description="AVAS selection threshold.")
    minao: str = Field(
        default="minao", min_length=1, description="Reference minimal basis for AVAS."
    )
    with_iao: bool = Field(default=False, description="Enable IAO in AVAS when supported.")
    openshell_option: int = Field(
        default=2, ge=0, le=10, description="PySCF AVAS openshell option."
    )
    canonicalize: bool = Field(default=True, description="Canonicalize AVAS orbitals.")
    ncore: int = Field(default=0, ge=0, le=512, description="Frozen core count for AVAS.")


class ChemistryCasscfSpec(ForbidExtraBase):
    orbital_optimization_audit: bool = Field(
        default=False,
        description="Run CASSCF orbital audit and record metadata.",
    )
    orbital_optimization_for_integrals: bool = Field(
        default=False,
        description="Rotate MOs with optimized CASSCF before active integrals.",
    )


class ChemistryBenchmarksSpec(ForbidExtraBase):
    enabled: bool = Field(default=False, description="Attach classical post-HF benchmark blocks.")
    backend: Literal["auto", "stub", "pyscf", "psi4"] = Field(
        default="auto",
        description="Backend for post-HF benchmarks.",
    )


class ChemistryPostHfSpec(ForbidExtraBase):
    integral_crosscheck: Literal["none", "pyscf_casci"] = Field(
        default="none",
        description="Optional integral crosscheck audit.",
    )
    rdm_correction_method: Literal[
        "none",
        "stub_nevpt2",
        "stub_ac0",
        "pyscf_nevpt2_casci",
        "psi4_nevpt2_casci",
    ] = Field(default="none", description="Post-SCF RDM correction hook.")


class ChemistryMoTransformSpec(ForbidExtraBase):
    hook: str = Field(default="", description="Post-SCF MO transform hook name.")
    kwargs: dict[str, Any] = Field(default_factory=dict, description="Opaque kwargs for MO hook.")


class ChemistrySymmetrySpec(ForbidExtraBase):
    pyscf_symmetry: bool | str = Field(
        default=False,
        description="PySCF gto.M symmetry argument on molecular branch.",
    )


class ChemistryMmChargesSpec(ForbidExtraBase):
    """Fixed partial charges for QM/MM bookkeeping (metadata; ONIOM demo reads via layers)."""

    atom_indices: list[int] = Field(
        default_factory=list,
        description="0-based atom indices receiving fixed MM charges.",
    )
    charges_e: list[float] = Field(
        default_factory=list,
        description="Partial charges in elementary charge units, parallel to atom_indices.",
    )

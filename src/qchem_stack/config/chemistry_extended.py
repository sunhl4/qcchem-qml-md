"""Extended chemistry driver knobs (nested YAML blocks).

Field reference: ``docs/config_校验分层约定.md`` §3.2.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from ._base import ForbidExtraBase
from ._chemistry_extended_validation import validate_pbc_mesh_and_cell
from .chemistry_extended_specs import (
    ChemistryAvasSpec,
    ChemistryBenchmarksSpec,
    ChemistryCasscfSpec,
    ChemistryMmChargesSpec,
    ChemistryMoTransformSpec,
    ChemistryPbcSpec,
    ChemistryPostHfSpec,
    ChemistrySolventSpec,
    ChemistrySymmetrySpec,
)


class ChemistryExtendedSpec(ForbidExtraBase):
    """Extended driver surface (parity-matrix-facing labels; PySCF where implemented)."""

    solvent: ChemistrySolventSpec = Field(default_factory=ChemistrySolventSpec)
    pbc: ChemistryPbcSpec = Field(default_factory=ChemistryPbcSpec)
    avas: ChemistryAvasSpec = Field(default_factory=ChemistryAvasSpec)
    casscf: ChemistryCasscfSpec = Field(default_factory=ChemistryCasscfSpec)
    benchmarks: ChemistryBenchmarksSpec = Field(default_factory=ChemistryBenchmarksSpec)
    post_hf: ChemistryPostHfSpec = Field(default_factory=ChemistryPostHfSpec)
    mo_transform: ChemistryMoTransformSpec = Field(default_factory=ChemistryMoTransformSpec)
    symmetry: ChemistrySymmetrySpec = Field(default_factory=ChemistrySymmetrySpec)
    mm_charges: ChemistryMmChargesSpec = Field(default_factory=ChemistryMmChargesSpec)

    @model_validator(mode="after")
    def _validate_pbc_cell_matrix(self) -> ChemistryExtendedSpec:
        validate_pbc_mesh_and_cell(self)
        mc = self.mm_charges
        if (mc.atom_indices or mc.charges_e) and len(mc.atom_indices) != len(mc.charges_e):
            raise ValueError(
                "chemistry_extended.mm_charges.atom_indices and charges_e must have equal length"
            )
        return self

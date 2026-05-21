"""Extended chemistry driver knobs (nested YAML blocks).

Field reference: ``docs/config_校验分层约定.md`` §3.2.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ._chemistry_extended_validation import validate_pbc_mesh_and_cell
from .chemistry_extended_specs import (
    ChemistryAvasSpec,
    ChemistryBenchmarksSpec,
    ChemistryCasscfSpec,
    ChemistryMoTransformSpec,
    ChemistryPbcSpec,
    ChemistryPostHfSpec,
    ChemistrySolventSpec,
    ChemistrySymmetrySpec,
)

_FORBID = ConfigDict(extra="forbid")


class ChemistryExtendedSpec(BaseModel):
    """Extended driver surface (parity-matrix-facing labels; PySCF where implemented)."""

    model_config = _FORBID

    solvent: ChemistrySolventSpec = Field(default_factory=ChemistrySolventSpec)
    pbc: ChemistryPbcSpec = Field(default_factory=ChemistryPbcSpec)
    avas: ChemistryAvasSpec = Field(default_factory=ChemistryAvasSpec)
    casscf: ChemistryCasscfSpec = Field(default_factory=ChemistryCasscfSpec)
    benchmarks: ChemistryBenchmarksSpec = Field(default_factory=ChemistryBenchmarksSpec)
    post_hf: ChemistryPostHfSpec = Field(default_factory=ChemistryPostHfSpec)
    mo_transform: ChemistryMoTransformSpec = Field(default_factory=ChemistryMoTransformSpec)
    symmetry: ChemistrySymmetrySpec = Field(default_factory=ChemistrySymmetrySpec)

    @model_validator(mode="after")
    def _validate_pbc_cell_matrix(self) -> ChemistryExtendedSpec:
        validate_pbc_mesh_and_cell(self)
        return self

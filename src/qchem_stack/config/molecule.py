"""Molecule geometry schema and coordinate normalization helpers.

Experiment YAML may set ``molecule.geometry_file`` to load Cartesian coordinates from disk
before :class:`MoleculeSpec` is built; see :mod:`qchem_stack.config.geometry_files` and
:func:`qchem_stack.config.load_experiment_config`.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from qchem_stack.exceptions import ConfigurationError

from ._constants import ANGSTROM_TO_BOHR


class MoleculeSpec(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    symbols: list[str]
    coordinates: list[list[float]] | None = Field(
        default=None,
        validation_alias=AliasChoices("coordinates", "coordinates_bohr"),
        description=(
            "Atomic Cartesian coordinates in ``coordinate_unit``. "
            "YAML may use legacy key ``coordinates_bohr`` (values interpreted as Bohr unless "
            "``coordinate_unit`` is set explicitly)."
        ),
    )
    zmatrix: str | None = Field(
        default=None,
        validation_alias=AliasChoices("zmatrix", "z_matrix"),
        description=(
            "Optional Z-matrix molecular geometry text. When provided (and ``coordinates`` is omitted), "
            "it is converted to Cartesian Bohr coordinates internally."
        ),
    )
    coordinate_unit: Literal["angstrom", "bohr"] = Field(
        default="angstrom",
        description=(
            "Length unit for ``coordinates``. Defaults to **ångström** for the canonical ``coordinates`` key; "
            "if the legacy alias ``coordinates_bohr`` is used and this field is omitted, it defaults to **bohr**."
        ),
    )
    charge: int = 0
    multiplicity: int = 1
    basis: str = "sto-3g"
    ecp: str | dict[str, str] | None = None

    @model_validator(mode="before")
    @classmethod
    def _legacy_coordinates_bohr_unit(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)
        if "coordinates_bohr" in out and "coordinate_unit" not in out:
            out["coordinate_unit"] = "bohr"
        return out

    @model_validator(mode="after")
    def _validate_geometry_source(self) -> MoleculeSpec:
        if self.coordinates is None and not (self.zmatrix and self.zmatrix.strip()):
            raise ValueError(
                "molecule requires either coordinates/coordinates_bohr or a non-empty zmatrix."
            )
        if self.coordinates is not None and self.zmatrix:
            raise ValueError("molecule.coordinates and molecule.zmatrix are mutually exclusive.")
        return self

    def coordinates_in_bohr(self):
        """Positions as a float ndarray in Bohr (PySCF ``gto.M`` internal convention)."""
        import numpy as np

        if self.coordinates is not None:
            arr = np.asarray(self.coordinates, dtype=float)
            if self.coordinate_unit == "angstrom":
                return arr * ANGSTROM_TO_BOHR
            return arr.copy()
        try:
            from pyscf import gto
        except ImportError as exc:
            raise ConfigurationError(
                "molecule.zmatrix requires PySCF to convert internal coordinates to Cartesian Bohr."
            ) from exc
        mol = gto.M(
            atom=str(self.zmatrix),
            basis=str(self.basis),
            charge=int(self.charge),
            spin=int(self.multiplicity) - 1,
            unit="Angstrom",
            ecp=self.ecp,
            verbose=0,
        )
        return np.asarray(mol.atom_coords(unit="Bohr"), dtype=float)

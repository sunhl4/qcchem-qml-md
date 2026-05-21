"""Molecule geometry schema and coordinate normalization helpers.

Experiment YAML may set ``molecule.geometry_file`` to load Cartesian coordinates from disk
before :class:`MoleculeSpec` is built; see :mod:`qchem_stack.config.geometry_files` and
:func:`qchem_stack.config.load_experiment_config`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from qchem_stack.exceptions import ConfigurationError

from ._constants import ANGSTROM_TO_BOHR

if TYPE_CHECKING:
    import numpy as np

_FORBID = ConfigDict(extra="forbid")


class MoleculeSpec(BaseModel):
    model_config = _FORBID

    symbols: list[str]
    coordinates: list[list[float]] | None = Field(
        default=None,
        description="Atomic Cartesian coordinates in ``coordinate_unit``.",
    )
    zmatrix: str | None = Field(
        default=None,
        description=(
            "Optional Z-matrix molecular geometry text. When provided (and ``coordinates`` is omitted), "
            "it is converted to Cartesian Bohr coordinates internally."
        ),
    )
    coordinate_unit: Literal["angstrom", "bohr"] = Field(
        default="angstrom",
        description="Length unit for ``coordinates`` (default ångström).",
    )
    charge: int = Field(
        default=0,
        description="Total molecular charge (0 neutral; +1 cation; -1 anion). Forwarded to PySCF/Psi4.",
    )
    multiplicity: int = Field(
        default=1,
        ge=1,
        description=(
            "Spin multiplicity 2S+1 (singlet=1, doublet=2, triplet=3). "
            "PySCF ``gto.M(..., spin=multiplicity - 1)``."
        ),
    )
    basis: str = Field(
        default="sto-3g",
        min_length=1,
        description=(
            "Basis set name understood by the classical backend (e.g. sto-3g, 6-31g, lanl2dz). "
            "Use the same family label as ``ecp`` when an ECP is specified."
        ),
    )
    ecp: str | dict[str, str] | None = Field(
        default=None,
        description=(
            "Effective core potential: ``None`` for all-electron; a ``str`` applies one ECP label to "
            "every atom; a ``dict`` maps element symbols to per-element ECP names (PySCF ``ecp=``)."
        ),
    )

    @model_validator(mode="after")
    def _validate_geometry_source(self) -> MoleculeSpec:
        if self.coordinates is None and not (self.zmatrix and self.zmatrix.strip()):
            raise ValueError("molecule requires either coordinates or a non-empty zmatrix.")
        if self.coordinates is not None and self.zmatrix:
            raise ValueError("molecule.coordinates and molecule.zmatrix are mutually exclusive.")
        return self

    def coordinates_in_bohr(self) -> np.ndarray:
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

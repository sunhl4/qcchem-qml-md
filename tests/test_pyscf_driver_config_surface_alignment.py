"""D38: `inquanto_driver_surface` YAML fragments reference real `ChemistryExtendedSpec` fields."""

from __future__ import annotations

from qchem_stack.chem.inquanto_driver_surface import INQUANTO_DRIVER_ALIAS_TO_CONFIG
from qchem_stack.config import ChemistryExtendedSpec

_FIELDS = set(ChemistryExtendedSpec.model_fields)


def test_driver_alias_strings_reference_extended_fields() -> None:
    for alias, spec in INQUANTO_DRIVER_ALIAS_TO_CONFIG.items():
        if "solvent_model" in spec:
            assert "solvent_model" in _FIELDS, alias
        if "pbc_cell_vectors_bohr" in spec:
            assert "pbc_cell_vectors_bohr" in _FIELDS, alias
        if "pbc_kpoint_mesh" in spec:
            assert "pbc_kpoint_mesh" in _FIELDS, alias

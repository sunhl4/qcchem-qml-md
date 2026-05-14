from __future__ import annotations

import pytest

from qchem_stack.config._active_space_validation import (
    normalize_active_space_entry,
    validate_frozen_orbitals,
    validate_jw_optimizer_flags,
)
from qchem_stack.config._chemistry_extended_validation import validate_pbc_mesh_and_cell
from qchem_stack.config._embedding_validation import nonempty_fragment_labels
from qchem_stack.config._experiment_validation import (
    preprocess_top_level_yaml_dict,
    validate_md_ml_extra_geometry_shape,
)
from qchem_stack.config._quantum_validation import validate_vqd_max_overlap_warn_nonneg
from qchem_stack.config.active_space import ActiveSpaceSpec
from qchem_stack.config.chemistry_extended import ChemistryExtendedSpec


def test_preprocess_top_level_yaml_dict_merges_unknown_into_extra() -> None:
    raw = {"experiment_id": "e", "extra": {"x": 1}, "unknown_beta": 2}
    out = preprocess_top_level_yaml_dict(raw, known_fields={"experiment_id", "extra"})
    assert out == {"experiment_id": "e", "extra": {"x": 1, "unknown_beta": 2}}


def test_validate_md_ml_extra_geometry_shape_requires_three_columns() -> None:
    with pytest.raises(ValueError, match="expected 3 Cartesian floats"):
        validate_md_ml_extra_geometry_shape(
            [[0.0, 0.0], [0.0, 0.0, 1.0]],
            geometry_index=0,
            n_atom=2,
        )


def test_validate_vqd_max_overlap_warn_nonneg() -> None:
    assert validate_vqd_max_overlap_warn_nonneg(0.1) == 0.1
    with pytest.raises(ValueError, match="must be >= 0"):
        validate_vqd_max_overlap_warn_nonneg(-0.1)


def test_nonempty_fragment_labels_strips_blanks() -> None:
    assert nonempty_fragment_labels(["a", " ", "", "b"]) == ["a", "b"]


def test_validate_frozen_orbitals_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="must not contain duplicates"):
        validate_frozen_orbitals([0, 0, 1])


def test_validate_jw_optimizer_flags_requires_jw_mapping() -> None:
    spec = ActiveSpaceSpec(
        strategy="cas",
        ncas=2,
        nelecas=2,
        fermion_qubit_mapping="jordan_wigner",
    )
    spec.prefer_restricted_spatial_fermion_for_jordan_wigner = True
    spec.fermion_qubit_mapping = "bravyi_kitaev"
    with pytest.raises(
        ValueError, match="requires active_space.fermion_qubit_mapping='jordan_wigner'"
    ):
        validate_jw_optimizer_flags(spec)


def test_normalize_active_space_entry_manual_sets_ncas_aliases() -> None:
    spec = ActiveSpaceSpec(
        strategy="manual",
        n_active_orbitals=3,
        n_active_electrons=2,
    )
    normalize_active_space_entry(spec)
    assert spec.ncas == 3
    assert spec.nelecas == 2


def test_validate_pbc_mesh_and_cell_requires_three_mesh_values() -> None:
    spec = ChemistryExtendedSpec()
    spec.pbc_kpoint_mesh = [1, 1]
    with pytest.raises(ValueError, match="must contain 3 integers >= 1"):
        validate_pbc_mesh_and_cell(spec)

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config._active_space_validation import (
    normalize_active_space_entry,
    validate_frozen_orbitals,
    validate_jw_optimizer_flags,
)
from qchem_stack.config._chemistry_extended_validation import validate_pbc_mesh_and_cell
from qchem_stack.config._embedding_validation import nonempty_fragment_labels_from_list
from qchem_stack.config._experiment_validation import (
    preprocess_top_level_yaml_dict,
    validate_md_ml_extra_geometry_shape,
)
from qchem_stack.config._quantum_validation import validate_vqd_max_overlap_warn_nonneg
from qchem_stack.config.active_space import ActiveSpaceSpec
from qchem_stack.config.chemistry_extended import ChemistryExtendedSpec
from qchem_stack.config.quantum import QuantumSpec
from qchem_stack.exceptions import ConfigurationError


def test_preprocess_top_level_yaml_dict_merges_unknown_into_extra() -> None:
    raw = {"experiment_id": "e", "extra": {"x": 1}, "unknown_beta": 2}
    out = preprocess_top_level_yaml_dict(raw, known_fields={"experiment_id", "extra"})
    assert out == {"experiment_id": "e", "extra": {"x": 1, "unknown_beta": 2}}


def test_preprocess_top_level_yaml_dict_strict_rejects_unknown() -> None:
    raw = {"experiment_id": "e", "unknown_beta": 2}
    with pytest.raises(ConfigurationError, match="Unknown top-level config keys"):
        preprocess_top_level_yaml_dict(
            raw,
            known_fields={"experiment_id", "extra"},
            strict_unknown_top_level=True,
        )


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
    assert nonempty_fragment_labels_from_list(["a", " ", "", "b"]) == ["a", "b"]


def test_validate_frozen_orbitals_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="must not contain duplicates"):
        validate_frozen_orbitals([0, 0, 1])


def test_validate_jw_optimizer_flags_requires_jw_mapping() -> None:
    from qchem_stack.config.active_space_mapping_specs import ActiveSpaceMappingSpec
    from qchem_stack.config.active_space_specs import ActiveSpaceCasSpec, ActiveSpaceJwSpec

    spec = ActiveSpaceSpec.model_construct(
        strategy="cas",
        mapping=ActiveSpaceMappingSpec(fermion_qubit="bravyi_kitaev"),
        cas=ActiveSpaceCasSpec(n_orbitals=2, n_electrons=2),
        jw=ActiveSpaceJwSpec(prefer_restricted_spatial=True),
    )
    with pytest.raises(ValueError, match="mapping.fermion_qubit='jordan_wigner'"):
        validate_jw_optimizer_flags(spec)


def test_normalize_active_space_entry_manual_sets_canonical_counts() -> None:
    spec = ActiveSpaceSpec.model_validate(
        {
            "strategy": "manual",
            "manual": {"n_orbitals": 3, "n_electrons": 2},
        }
    )
    normalize_active_space_entry(spec)
    assert spec.cas.n_orbitals == 3
    assert spec.cas.n_electrons == 2
    assert spec.manual.n_orbitals == 3
    assert spec.manual.n_electrons == 2


def test_validate_pbc_mesh_and_cell_requires_three_mesh_values() -> None:
    from qchem_stack.config.chemistry_extended_specs import ChemistryPbcSpec

    spec = ChemistryExtendedSpec.model_construct(pbc=ChemistryPbcSpec(kpoint_mesh=[1, 1]))
    with pytest.raises(ValueError, match="must contain 3 integers >= 1"):
        validate_pbc_mesh_and_cell(spec)


def test_mitigation_pmsv_requires_stabilizers_when_enabled() -> None:
    from qchem_stack.config import MitigationSpec

    with pytest.raises(ValueError, match="pmsv.stabilizers"):
        MitigationSpec.model_validate({"pmsv": {"enabled": True, "stabilizers": []}})


def test_quantum_nested_blocks_roundtrip() -> None:
    spec = QuantumSpec.model_validate(
        {
            "algorithm": "vqe",
            "vqe": {"depth": 2, "maxiter": 50},
            "pauli": {"use_protocol": False},
        }
    )
    assert spec.vqe.depth == 2
    assert spec.vqe.maxiter == 50
    assert spec.pauli.use_protocol is False


def test_quantum_forbids_unknown_nested_keys() -> None:
    with pytest.raises(ValidationError):
        QuantumSpec.model_validate({"vqe": {"depth": 1, "unknown_knob": 1}})


def test_embedding_fragment_labels_rejects_non_list() -> None:
    from qchem_stack.config.embedding_specs import DmetEmbeddingSpec

    with pytest.raises(ValueError, match="fragment_labels must be a list"):
        DmetEmbeddingSpec.model_validate({"fragment_labels": "frag_a"})


def test_embedding_forbids_unknown_top_level_keys() -> None:
    from qchem_stack.config.embedding_specs import EmbeddingNone

    with pytest.raises(ValidationError):
        EmbeddingNone.model_validate({"mode": "none", "unknown_embedding_knob": 1})


def test_backend_forbids_unknown_keys() -> None:
    from qchem_stack.config.backend import BackendSpecConfig

    with pytest.raises(ValidationError):
        BackendSpecConfig.model_validate({"provider": "statevector", "typo_field": True})


def test_embedding_dmet_rhf_suggestion_in_error() -> None:
    from qchem_stack.config._embedding_validation import (
        EmbeddingValidationContext,
        validate_embedding,
    )
    from qchem_stack.config.embedding_specs import EmbeddingDmet

    spec = EmbeddingDmet.model_validate(
        {
            "mode": "dmet",
            "dmet": {
                "hamiltonian_source": "schmidt_atomic_production",
                "schmidt": {
                    "dmet_max_cycles": 2,
                    "fragment_atom_indices": [0, 1],
                },
            },
        }
    )
    ctx = EmbeddingValidationContext(n_atom=2, scf_method="UHF", scf_driver="pyscf")
    with pytest.raises(ConfigurationError, match="Suggestion:.*embedding_dmet"):
        validate_embedding(spec, ctx)

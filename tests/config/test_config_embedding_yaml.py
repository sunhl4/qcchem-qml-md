"""ExperimentConfig loads packaged YAML with ``embedding`` block."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.exceptions import ConfigurationError
from tests.helpers.paths import configs_path

_CAS = {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
_MOLECULE = {
    "symbols": ["H", "H"],
    "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
    "coordinate_unit": "bohr",
}


def test_example_h2_yaml_has_embedding_none() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    assert cfg.embedding.mode == "none"


def test_load_config_invalid_yaml_raises_configuration_error(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("[ unclosed", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="Invalid YAML"):
        load_experiment_config(p)


def test_load_config_non_mapping_raises_configuration_error(tmp_path: Path) -> None:
    p = tmp_path / "list.yaml"
    p.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="mapping"):
        load_experiment_config(p)


def test_projection_mulliken_requires_non_empty_fragment_atoms() -> None:
    raw = {
        "schema_version": "2",
        "experiment_id": "e",
        "random_seed": 0,
        "molecule": _MOLECULE,
        "active_space": _CAS,
        "embedding": {
            "mode": "projection",
            "projection": {
                "quantum_hamiltonian": "fragment_mulliken_mo",
                "fragment_atom_indices": [],
            },
        },
    }
    with pytest.raises(ValidationError):
        ExperimentConfig.from_yaml_dict(raw)


def test_projection_mulliken_requires_projection_mode() -> None:
    raw = {
        "schema_version": "2",
        "experiment_id": "e",
        "random_seed": 0,
        "molecule": _MOLECULE,
        "active_space": _CAS,
        "embedding": {
            "mode": "none",
            "projection": {
                "quantum_hamiltonian": "fragment_mulliken_mo",
                "fragment_atom_indices": [0],
            },
        },
    }
    with pytest.raises(ValidationError):
        ExperimentConfig.from_yaml_dict(raw)


def test_projection_fragment_atom_index_out_of_range() -> None:
    raw = {
        "schema_version": "2",
        "experiment_id": "e",
        "random_seed": 0,
        "molecule": _MOLECULE,
        "active_space": _CAS,
        "embedding": {
            "mode": "projection",
            "projection": {
                "quantum_hamiltonian": "fragment_mulliken_mo",
                "fragment_atom_indices": [0, 2],
            },
        },
    }
    with pytest.raises(ValidationError, match="out of range"):
        ExperimentConfig.from_yaml_dict(raw)


def test_projection_mulliken_valid_config_loads() -> None:
    raw = {
        "schema_version": "2",
        "experiment_id": "e",
        "random_seed": 0,
        "molecule": _MOLECULE,
        "active_space": _CAS,
        "embedding": {
            "mode": "projection",
            "projection": {
                "quantum_hamiltonian": "fragment_mulliken_mo",
                "fragment_atom_indices": [0],
            },
        },
    }
    cfg = ExperimentConfig.from_yaml_dict(raw)
    assert cfg.embedding.projection.quantum_hamiltonian == "fragment_mulliken_mo"


def test_from_yaml_dict_merges_explicit_extra_and_unknown_top_level() -> None:
    raw = {
        "schema_version": "2",
        "experiment_id": "e",
        "random_seed": 0,
        "molecule": _MOLECULE,
        "active_space": _CAS,
        "extra": {"from_extra_block": 1},
        "unknown_alpha": "a",
        "unknown_beta": "b",
    }
    cfg = ExperimentConfig.from_yaml_dict(raw)
    assert cfg.extra == {
        "from_extra_block": 1,
        "unknown_alpha": "a",
        "unknown_beta": "b",
    }


def test_from_yaml_dict_rejects_non_mapping_extra() -> None:
    raw = {
        "schema_version": "2",
        "experiment_id": "e",
        "random_seed": 0,
        "molecule": _MOLECULE,
        "active_space": _CAS,
        "extra": ["not", "a", "mapping"],
    }
    with pytest.raises(TypeError, match="must be a mapping"):
        ExperimentConfig.from_yaml_dict(raw)

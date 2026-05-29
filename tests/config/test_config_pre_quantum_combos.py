"""Pre-quantum YAML combination guards (config load time)."""

from __future__ import annotations

import pytest

from qchem_stack.config import (
    ExperimentConfig,
    load_experiment_config,
    validate_pre_quantum_contract,
)
from qchem_stack.config._embedding_validation import SCHMIDT_DMET_MAX_CYCLES_LIMIT
from qchem_stack.exceptions import ConfigurationError
from tests.helpers.paths import configs_path


def _h2_base() -> dict:
    from tests.helpers.h2_yaml import h2_yaml_dict

    return h2_yaml_dict(experiment_id="combo_test")


def _schmidt_embedding(**schmidt_extra: object) -> dict:
    return {
        "mode": "dmet",
        "dmet": {
            "hamiltonian_source": "schmidt_atomic_production",
            "schmidt": {
                "fragment_atom_indices": [0],
                "n_bath_spatial": 1,
                "max_impurity_spatial_orbitals": 4,
                **schmidt_extra,
            },
        },
    }


def test_pyscf_none_canonical_path_loads() -> None:
    cfg = ExperimentConfig.from_yaml_dict(_h2_base())
    assert cfg.scf.driver == "pyscf"


def test_precomputed_rejects_benchmark() -> None:
    data = _h2_base()
    data["scf"] = {
        "driver": "precomputed",
        "precomputed": {"bundle_path": "/tmp/nonexistent.json"},
    }
    data["chemistry_extended"] = {"benchmarks": {"enabled": True}}
    with pytest.raises(ConfigurationError, match="benchmarks.enabled"):
        ExperimentConfig.from_yaml_dict(data)


def test_precomputed_rejects_rdm_correction() -> None:
    data = _h2_base()
    data["scf"] = {
        "driver": "precomputed",
        "precomputed": {"bundle_path": "/tmp/nonexistent.json"},
    }
    data["chemistry_extended"] = {"post_hf": {"rdm_correction_method": "stub_nevpt2"}}
    with pytest.raises(ConfigurationError, match="rdm_correction_method"):
        ExperimentConfig.from_yaml_dict(data)


def test_schmidt_requires_rhf_at_config_time() -> None:
    data = _h2_base()
    data["scf"]["method"] = "UHF"
    data["embedding"] = _schmidt_embedding()
    with pytest.raises(ConfigurationError, match="schmidt_atomic_production"):
        ExperimentConfig.from_yaml_dict(data)


def test_schmidt_cycle_limit() -> None:
    data = _h2_base()
    data["embedding"] = _schmidt_embedding(
        dmet_max_cycles=SCHMIDT_DMET_MAX_CYCLES_LIMIT + 1,
    )
    with pytest.raises(ConfigurationError, match="dmet_max_cycles exceeds"):
        ExperimentConfig.from_yaml_dict(data)


def test_schmidt_rejects_uhf_at_config_time() -> None:
    data = _h2_base()
    data["scf"]["method"] = "UHF"
    data["embedding"] = _schmidt_embedding()
    with pytest.raises(ConfigurationError, match="schmidt_atomic_production"):
        ExperimentConfig.from_yaml_dict(data)


def test_example_h2_yaml_still_loads() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    assert cfg.scf.driver == "pyscf"


def test_psi4_schmidt_yaml_loads() -> None:
    cfg = load_experiment_config(configs_path("example_h2_psi4_schmidt_dmet.yaml"))
    assert cfg.scf.driver == "psi4"
    validate_pre_quantum_contract(cfg)


def test_psi4_avas_yaml_loads() -> None:
    cfg = load_experiment_config(configs_path("example_h2_psi4_avas.yaml"))
    assert cfg.scf.driver == "psi4"
    assert cfg.active_space.strategy == "avas"
    validate_pre_quantum_contract(cfg)


def test_psi4_projection_mulliken_yaml_loads() -> None:
    cfg = load_experiment_config(configs_path("example_h2_psi4_projection_mulliken.yaml"))
    assert cfg.scf.driver == "psi4"
    assert cfg.embedding.projection.quantum_hamiltonian == "fragment_mulliken_mo"
    validate_pre_quantum_contract(cfg)


def test_precomputed_schmidt_rejected_by_capability() -> None:
    data = _h2_base()
    data["scf"] = {
        "driver": "precomputed",
        "precomputed": {"bundle_path": "configs/precomputed_classical_reference_h2.json"},
    }
    data["embedding"] = _schmidt_embedding()
    with pytest.raises(ConfigurationError, match="supports_schmidt_atomic_hamiltonian"):
        ExperimentConfig.from_yaml_dict(data)


def test_precomputed_projection_rejected_by_capability() -> None:
    data = _h2_base()
    data["scf"] = {
        "driver": "precomputed",
        "precomputed": {"bundle_path": "configs/precomputed_classical_reference_h2.json"},
    }
    data["embedding"] = {
        "mode": "projection",
        "projection": {
            "quantum_hamiltonian": "fragment_mulliken_mo",
            "fragment_atom_indices": [0, 1],
        },
    }
    with pytest.raises(
        ConfigurationError, match="supports_projection_fragment_mulliken_hamiltonian"
    ):
        ExperimentConfig.from_yaml_dict(data)

"""Pre-quantum YAML combination guards (config load time)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.config._experiment_validation import SCHMIDT_DMET_MAX_CYCLES_LIMIT
from qchem_stack.exceptions import ConfigurationError


def _h2_base() -> dict:
    return {
        "schema_version": "1",
        "experiment_id": "combo_test",
        "random_seed": 1,
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates_bohr": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "active_space": {
            "n_active_orbitals": 2,
            "n_active_electrons": 2,
        },
        "scf": {"driver": "pyscf", "method": "RHF"},
        "embedding": {"mode": "none"},
        "quantum": {"algorithm": "vqe", "vqe_depth": 1, "vqe_maxiter": 5},
    }


def test_pyscf_none_canonical_path_loads() -> None:
    cfg = ExperimentConfig.model_validate(_h2_base())
    assert cfg.scf.driver == "pyscf"


def test_precomputed_rejects_benchmark() -> None:
    data = _h2_base()
    data["scf"] = {
        "driver": "precomputed",
        "precomputed_bundle_path": "/tmp/nonexistent.json",
    }
    data["chemistry_extended"] = {"classical_benchmark_enabled": True}
    with pytest.raises(ConfigurationError, match="classical_benchmark_enabled"):
        ExperimentConfig.model_validate(data)


def test_precomputed_rejects_rdm_correction() -> None:
    data = _h2_base()
    data["scf"] = {
        "driver": "precomputed",
        "precomputed_bundle_path": "/tmp/nonexistent.json",
    }
    data["chemistry_extended"] = {"rdm_correction_method": "stub_nevpt2"}
    with pytest.raises(ConfigurationError, match="rdm_correction_method"):
        ExperimentConfig.model_validate(data)


def test_schmidt_requires_rhf_at_config_time() -> None:
    data = _h2_base()
    data["scf"]["method"] = "UHF"
    data["embedding"] = {
        "mode": "dmet",
        "dmet_hamiltonian_source": "schmidt_atomic_production",
        "schmidt_fragment_atom_indices": [0],
        "schmidt_n_bath_spatial": 1,
        "schmidt_max_impurity_spatial_orbitals": 4,
    }
    with pytest.raises(ConfigurationError, match="schmidt_atomic_production"):
        ExperimentConfig.model_validate(data)


def test_schmidt_cycle_limit() -> None:
    data = _h2_base()
    data["embedding"] = {
        "mode": "dmet",
        "dmet_hamiltonian_source": "schmidt_atomic_production",
        "schmidt_fragment_atom_indices": [0],
        "schmidt_n_bath_spatial": 1,
        "schmidt_max_impurity_spatial_orbitals": 4,
        "schmidt_dmet_max_cycles": SCHMIDT_DMET_MAX_CYCLES_LIMIT + 1,
    }
    with pytest.raises(ConfigurationError, match="schmidt_dmet_max_cycles exceeds"):
        ExperimentConfig.model_validate(data)


def test_psi4_rejects_schmidt_at_config_time() -> None:
    data = _h2_base()
    data["scf"]["driver"] = "psi4"
    data["embedding"] = {
        "mode": "dmet",
        "dmet_hamiltonian_source": "schmidt_atomic_production",
        "schmidt_fragment_atom_indices": [0],
        "schmidt_n_bath_spatial": 1,
        "schmidt_max_impurity_spatial_orbitals": 4,
    }
    with pytest.raises(ConfigurationError, match="Schmidt support"):
        ExperimentConfig.model_validate(data)


def test_example_h2_yaml_still_loads() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    assert cfg.scf.driver == "pyscf"

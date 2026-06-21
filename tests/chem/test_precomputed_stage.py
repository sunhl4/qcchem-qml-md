from __future__ import annotations

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.precomputed_stage import (
    precomputed_config_fingerprint,
    precomputed_config_fingerprint_payload,
)
from tests.helpers.paths import configs_path


def test_precomputed_config_fingerprint_is_stable_for_same_config() -> None:
    cfg = load_experiment_config(configs_path("example_h2_precomputed_bundle.yaml"))
    fp1 = precomputed_config_fingerprint(cfg)
    fp2 = precomputed_config_fingerprint(cfg)
    assert fp1 == fp2
    assert len(fp1) == 64


def test_precomputed_config_fingerprint_payload_includes_active_space_and_geometry() -> None:
    cfg = load_experiment_config(configs_path("example_h2_precomputed_bundle.yaml"))
    payload = precomputed_config_fingerprint_payload(cfg)
    assert payload["schema"] == "precomputed_config_fingerprint_v1"
    assert payload["active_space"]["n_active_orbitals"] == 2
    assert payload["active_space"]["fermion_qubit_mapping"] == "jordan_wigner"
    assert payload["molecule_symbols"] == ["H", "H"]

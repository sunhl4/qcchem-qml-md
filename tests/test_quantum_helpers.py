from __future__ import annotations

from qchem_stack.config import ExperimentConfig
from qchem_stack.config.quantum_helpers import (
    excited_vqd_after_variational,
    pauli_protocol_enabled,
    quantum_repro_core_fields,
    resolve_vqe_maxiter,
)


def test_resolve_vqe_maxiter_from_nested_quantum() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"vqe": {"maxiter": 42}},
        }
    )
    assert resolve_vqe_maxiter(cfg) == 42


def test_pauli_protocol_enabled() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"pauli": {"use_protocol": False}},
        }
    )
    assert pauli_protocol_enabled(cfg) is False


def test_excited_vqd_after_variational_default_false() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
        }
    )
    assert excited_vqd_after_variational(cfg) is False


def test_quantum_repro_core_fields_includes_algorithm() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "t",
            "molecule": {"symbols": ["H", "H"], "coordinates": [[0, 0, 0], [0, 0, 0.74]]},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "quantum": {"algorithm": "vqe", "vqe": {"maxiter": 10}},
        }
    )
    fields = quantum_repro_core_fields(cfg)
    assert fields["quantum_algorithm"] == "vqe"
    assert fields["vqe_maxiter"] == 10

"""QuantumSpec: mutually exclusive Pauli shot modes."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config import ExperimentConfig


def _minimal_cfg(**pauli_overrides) -> dict:
    return {
        "schema_version": "2",
        "experiment_id": "t",
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates": [[0, 0, 0], [0, 0, 1.4]],
            "coordinate_unit": "bohr",
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "active_space": {
            "strategy": "cas",
            "cas": {"n_orbitals": 2, "n_electrons": 2},
        },
        "quantum": {
            "algorithm": "vqe",
            "vqe": {"depth": 1, "maxiter": 1},
            "pauli": pauli_overrides,
        },
    }


def test_cannot_set_both_sampled_and_qiskit_shots() -> None:
    with pytest.raises(ValidationError):
        ExperimentConfig.from_yaml_dict(
            _minimal_cfg(
                run_sampled=True,
                run_qiskit_shots=True,
            )
        )


def test_both_off_ok() -> None:
    c = ExperimentConfig.from_yaml_dict(
        _minimal_cfg(
            run_sampled=False,
            run_qiskit_shots=False,
        )
    )
    assert c.quantum.pauli.run_sampled is False

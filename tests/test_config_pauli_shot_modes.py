"""QuantumSpec: mutually exclusive Pauli shot modes."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config import ExperimentConfig


def _minimal_cfg(**quantum_overrides) -> dict:
    return {
        "experiment_id": "t",
        "molecule": {
            "symbols": ["H", "H"],
            "coordinates_bohr": [[0, 0, 0], [0, 0, 1.4]],
            "charge": 0,
            "multiplicity": 1,
            "basis": "sto-3g",
        },
        "active_space": {"n_active_orbitals": 2, "n_active_electrons": 2},
        "quantum": {"algorithm": "vqe", "vqe_depth": 1, "vqe_maxiter": 1, **quantum_overrides},
    }


def test_cannot_set_both_sampled_and_qiskit_shots() -> None:
    with pytest.raises(ValidationError):
        ExperimentConfig.model_validate(
            _minimal_cfg(
                run_sampled_pauli_protocol=True,
                run_qiskit_shots_pauli_protocol=True,
            )
        )


def test_both_off_ok() -> None:
    c = ExperimentConfig.model_validate(
        _minimal_cfg(
            run_sampled_pauli_protocol=False,
            run_qiskit_shots_pauli_protocol=False,
        )
    )
    assert c.quantum.run_qiskit_shots_pauli_protocol is False

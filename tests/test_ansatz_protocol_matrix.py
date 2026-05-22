"""Runtime guards for ansatz × protocol matrix (P1 enforcement)."""

from __future__ import annotations

import pytest

from qchem_stack.config import ActiveSpaceSpec, ExperimentConfig, MoleculeSpec, QuantumSpec
from qchem_stack.protocols.product_contract import (
    matrix_pauli_protocol_name,
    matrix_qse_protocol_name,
    validate_ansatz_protocol_combo,
    validate_pauli_protocol_for_config,
    validate_qse_protocol_for_config,
)


def _cfg(**q_patch: object) -> ExperimentConfig:
    base = {
        "pauli": {"use_protocol": True, "run_sampled": False, "run_qiskit_shots": False},
        "variational": {"ansatz": "hea"},
    }
    base.update(q_patch)  # type: ignore[arg-type]
    return ExperimentConfig(
        experiment_id="t",
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        quantum=QuantumSpec.model_validate(base),
    )


def test_matrix_pauli_protocol_name_exact() -> None:
    cfg = _cfg()
    assert matrix_pauli_protocol_name(cfg) == "pauli_averaging_exact"


def test_validate_pauli_uccsd_zne_fold_rejected() -> None:
    _cfg(variational={"ansatz": "uccsd"})
    with pytest.raises(ValueError, match="unsupported"):
        validate_ansatz_protocol_combo("uccsd", "zne_circuit_scale_fold")


def test_validate_qse_uccsd_qiskit_allowed() -> None:
    cfg = _cfg(
        variational={"ansatz": "uccsd"},
        excited={"qse": {"shot_mode": "pauli_transitions_qiskit"}},
    )
    validate_qse_protocol_for_config(cfg, ansatz="uccsd", shot_mode="pauli_transitions_qiskit")


def test_validate_qse_exact_skips_matrix() -> None:
    cfg = _cfg(excited={"qse": {"shot_mode": "exact"}})
    validate_qse_protocol_for_config(cfg, ansatz="hea", shot_mode="exact")


def test_matrix_qse_protocol_name_mapping() -> None:
    assert matrix_qse_protocol_name("pauli_transitions_qiskit") == "qse_pauli_transitions_qiskit"
    assert matrix_qse_protocol_name("gaussian_h") == "qse_pauli_transitions"


def test_validate_pauli_for_config_hea_sampled() -> None:
    cfg = _cfg(pauli={"use_protocol": True, "run_sampled": True, "run_qiskit_shots": False})
    validate_pauli_protocol_for_config(cfg, ansatz="hea")

"""Cross-field validation helpers for :mod:`qchem_stack.config.quantum`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .quantum import QuantumSpec


def validate_algorithm_registered_or_factory(spec: QuantumSpec) -> None:
    from qchem_stack.quantum.variational_plugins.loader import validate_factory_import_path
    from qchem_stack.quantum.variational_plugins.registry import is_registered_variational_id

    if spec.algorithm_factory:
        validate_factory_import_path(spec.algorithm_factory)
        return
    if not is_registered_variational_id(spec.algorithm):
        raise ValueError(
            f"Unknown quantum.algorithm={spec.algorithm!r}. "
            "Use a built-in id or set quantum.algorithm_factory to an import path."
        )


def validate_pauli_shot_mode_mutually_exclusive(spec: QuantumSpec) -> None:
    pauli = spec.pauli
    if pauli.run_sampled and pauli.run_qiskit_shots:
        raise ValueError(
            "Set only one of quantum.pauli.run_sampled (statevector MC) and "
            "quantum.pauli.run_qiskit_shots (Qiskit bitstrings), not both."
        )


def validate_uccsd_trotter_steps(spec: QuantumSpec) -> None:
    trotter_steps = spec.variational.uccsd_trotter_steps
    if trotter_steps is None:
        return
    if spec.variational.ansatz != "uccsd":
        raise ValueError(
            "quantum.variational.uccsd_trotter_steps is only valid when variational.ansatz='uccsd'."
        )
    if int(trotter_steps) < 1:
        raise ValueError("quantum.variational.uccsd_trotter_steps must be >= 1 when set.")


def validate_vqd_penalty_weights_len(spec: QuantumSpec) -> None:
    vqd = spec.excited.vqd
    penalty_weights = vqd.penalty_weights
    if penalty_weights is None:
        return
    expected_len = max(0, int(vqd.n_states) - 1)
    if len(penalty_weights) != expected_len:
        raise ValueError(
            "quantum.excited.vqd.penalty_weights must have length n_states - 1 "
            f"({expected_len}), got {len(penalty_weights)}"
        )


def validate_vqd_max_overlap_warn_nonneg(value: float | None) -> float | None:
    if value is None:
        return None
    normalized = float(value)
    if normalized < 0.0:
        raise ValueError("quantum.excited.vqd.max_overlap_warn must be >= 0 when set")
    return normalized

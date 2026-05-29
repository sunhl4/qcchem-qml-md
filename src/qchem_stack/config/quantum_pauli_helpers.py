"""Pauli protocol path classification and config resolvers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .experiment import ExperimentConfig


PAULI_PATH_DISABLED = "pauli_protocol_disabled"
PAULI_PATH_EXACT = "exact_executor"
PAULI_PATH_STATEVECTOR_SHOT_SIM = "statevector_grouped_shot_simulation"
PAULI_PATH_QISKIT_COUNTS = "qiskit_get_counts_bitstrings"


def pauli_protocol_enabled(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.use_protocol)


def pauli_run_sampled(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.run_sampled)


def pauli_run_qiskit_shots(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.run_qiskit_shots)


def resolve_pauli_grouping(
    cfg: ExperimentConfig,
) -> Literal["tensor_product", "greedy_commuting"]:
    return cfg.quantum.pauli.grouping


def pauli_record_histograms(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.record_histograms)


def resolve_pauli_support_max_terms(cfg: ExperimentConfig) -> int | None:
    return cfg.quantum.pauli.support_max_terms


def classify_pauli_expectation_path_from_flags(
    *,
    use_protocol: bool,
    run_sampled: bool,
    run_qiskit_shots: bool,
) -> str:
    if not use_protocol:
        return PAULI_PATH_DISABLED
    if run_sampled and run_qiskit_shots:
        raise ValueError(
            "run_sampled_pauli_protocol and run_qiskit_shots_pauli_protocol are mutually exclusive"
        )
    if run_sampled:
        return PAULI_PATH_STATEVECTOR_SHOT_SIM
    if run_qiskit_shots:
        return PAULI_PATH_QISKIT_COUNTS
    return PAULI_PATH_EXACT


def classify_pauli_expectation_path_for_config(cfg: ExperimentConfig) -> str:
    return classify_pauli_expectation_path_from_flags(
        use_protocol=pauli_protocol_enabled(cfg),
        run_sampled=pauli_run_sampled(cfg),
        run_qiskit_shots=pauli_run_qiskit_shots(cfg),
    )

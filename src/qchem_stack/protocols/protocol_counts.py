"""Typed shapes for Pauli protocol ``protocol_counts`` export blocks."""

from __future__ import annotations

from typing import Any, TypedDict


class ProtocolCountsCore(TypedDict, total=False):
    expectation: float
    expectation_source: str
    energy_stderr_model: str
    raw_shots: int
    shots_per_circuit_effective: int
    energy_stderr: float
    n_measurement_circuits: int
    total_shots_budget: int
    n_pauli_terms: int
    n_pauli_groups: int
    pmsv_stderr_scale: float


class ProtocolCountsPauliSupport(TypedDict, total=False):
    hamiltonian_pauli_term_records: list[dict[str, Any]]
    hamiltonian_pauli_strings: list[str]
    n_hamiltonian_pauli_terms: int
    pauli_support_truncated: bool
    n_hamiltonian_pauli_terms_full: int
    pauli_group_ids: list[int]


class ProtocolCountsZne(TypedDict, total=False):
    zne_curve: list[float]
    zne_energies: list[float]
    zne_mode: str
    zne_extrapolated_energy: float
    zne_circuit_fold_fallback_reason: str


class ProtocolCountsPmsv(TypedDict, total=False):
    kept_shots: int
    pmsv_report: dict[str, Any]


def empty_protocol_counts() -> dict[str, Any]:
    return {}

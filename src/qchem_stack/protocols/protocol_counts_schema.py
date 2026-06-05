"""Typed shapes for protocol stage export mirrors (parity / Methods)."""

from __future__ import annotations

from typing import TypedDict


class ProtocolCountsExportV1(TypedDict, total=False):
    """Subset of keys written by ``PauliAveragingProtocol`` / pipeline ``protocol_counts``."""

    expectation_source: str
    energy_stderr_model: str
    n_hamiltonian_pauli_terms: int
    n_pauli_groups: int
    n_circuits: int
    hamiltonian_pauli_strings: list[str]
    pauli_group_ids: list[str]
    pmsv_report: dict[str, object]
    zne_energies: list[float]
    zne_mode: str


class ResourceRowExportV1(TypedDict, total=False):
    """One row of ``dataframe_circuit_shot`` / resource ledger export."""

    circuit_id: str
    n_shots: int
    depth_proxy: int
    group_id: str

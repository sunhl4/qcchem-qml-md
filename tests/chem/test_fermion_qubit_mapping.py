"""Fermion→qubit mapping (JW / BK / SCBK) wiring and parity metadata."""

from __future__ import annotations

import numpy as np

from qchem_stack.chem.hamiltonian import (
    hamiltonian_fingerprint_from_qubit_operator,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)


def test_bk_and_jw_fingerprints_differ_on_two_electron_integral_model() -> None:
    h1 = np.eye(2)
    h2 = np.zeros((2, 2, 2, 2))
    qh_jw = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="jordan_wigner"
    )
    qh_bk = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="bravyi_kitaev"
    )
    assert qh_jw.meta["fermion_to_qubit_map"] == "jordan_wigner"
    assert qh_bk.meta["fermion_to_qubit_map"] == "bravyi_kitaev"


def test_symmetry_conserving_bravyi_kitaev_reduces_qubit_count() -> None:
    from openfermion import count_qubits

    h1 = np.diag([0.1, 0.2]).astype(float)
    h2 = np.zeros((2, 2, 2, 2))
    qh_jw = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="jordan_wigner"
    )
    qh_sc = qubit_hamiltonian_from_spatial_chemist_integrals(
        0.0, h1, h2, 2, fermion_qubit_mapping="symmetry_conserving_bravyi_kitaev"
    )
    assert count_qubits(qh_jw.operator) == 4
    assert qh_jw.n_qubits == 4
    assert count_qubits(qh_sc.operator) == 2
    assert qh_sc.n_qubits == 2
    assert qh_sc.meta["fermion_to_qubit_map"] == "symmetry_conserving_bravyi_kitaev"
    fp_jw, _ = hamiltonian_fingerprint_from_qubit_operator(qh_jw.operator)
    fp_sc, _ = hamiltonian_fingerprint_from_qubit_operator(qh_sc.operator)
    assert fp_jw != fp_sc


def test_ansatz_registry_is_deterministic() -> None:
    from qchem_stack.quantum.ansatz_registry import ANSATZ_REGISTRY, list_registered_ansatz_ids

    assert list_registered_ansatz_ids() == tuple(sorted(ANSATZ_REGISTRY.keys()))


def test_documented_fermion_mappings_includes_scbk() -> None:
    from qchem_stack.chem.fermion_mapping_registry import list_documented_fermion_qubit_mappings

    assert "symmetry_conserving_bravyi_kitaev" in list_documented_fermion_qubit_mappings()


def test_public_mapping_alias_surface_v1_stable() -> None:
    """L1 table: tutorial nicknames vs YAML literals; JKMN/HCB executable."""
    from qchem_stack.chem.fermion_mapping_registry import (
        DOCUMENTED_FERMION_QUBIT_MAPPINGS,
        public_mapping_alias_surface_v1,
    )
    from qchem_stack.contracts.schema_ids import PUBLIC_MAPPING_ALIAS_SURFACE_V1

    blob = public_mapping_alias_surface_v1()
    assert blob["schema"] == PUBLIC_MAPPING_ALIAS_SURFACE_V1
    assert blob["qchem_stack_documented_literals"] == list(DOCUMENTED_FERMION_QUBIT_MAPPINGS)
    rows = blob["tutorial_alias_rows"]
    assert len(rows) == 5 and all(r["executable"] for r in rows)
    bad = blob["not_executable_named_in_research_stack"]
    assert bad == []
    status_rows = blob.get("mapping_status_rows_v1")
    assert isinstance(status_rows, list) and status_rows
    assert any(r.get("execution_status") == "executable" for r in status_rows)
    assert "jkmn" in blob["qchem_stack_documented_literals"]


def test_algorithm_registry_sorted_ids() -> None:
    from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids

    assert list_registered_algorithm_ids() == (
        "adapt",
        "iqcc",
        "iqeb",
        "qpe_deterministic",
        "qpe_info_theory",
        "qpe_kitaev",
        "sa_vqe",
        "tetris_adapt",
        "vqe",
    )

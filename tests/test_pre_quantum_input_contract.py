from __future__ import annotations

from types import SimpleNamespace

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.chem.pre_quantum_input import (
    PreQuantumInput,
    pre_quantum_meta_from_hamiltonian,
)
from qchem_stack.chem.system import MolecularSystem


def _reference() -> ClassicalMeanFieldReference:
    return ClassicalMeanFieldReference(
        mf=None,
        e_tot=0.0,
        mo_energy=np.zeros(1, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"],
            coordinates_bohr=np.zeros((1, 3), dtype=float),
        ),
        driver_meta={"upstream_classical_software_tag": "mock_solver"},
    )


def test_pre_quantum_summary_exposes_stable_handoff_fields() -> None:
    qh = QubitHamiltonian(
        operator=QubitOperator("Z0", 1.0),
        n_qubits=1,
        meta={
            "integral_source": "mock_solver_active_space",
            "integral_openfermion_bridge": "mock_solver_openfermion_interaction_operator_v1",
            "fermion_to_qubit_map": "jordan_wigner",
            "hamiltonian_fingerprint": "abc123",
            "n_active_orbitals": 1,
            "n_active_electrons": 1,
        },
    )
    pre_q = PreQuantumInput(
        classical_reference=_reference(),
        qubit_hamiltonian=qh,
        meta=pre_quantum_meta_from_hamiltonian(
            source="contract_test",
            qubit_hamiltonian=qh,
        ),
    )

    summary = pre_q.as_summary_dict()

    assert summary["schema"] == "pre_quantum_input_v1"
    assert summary["source"] == "contract_test"
    assert summary["backend_tag"] == "mock_solver"
    assert summary["integral_source"] == "mock_solver_active_space"
    assert summary["fermion_to_qubit_map"] == "jordan_wigner"
    assert summary["hamiltonian_fingerprint"] == "abc123"
    assert summary["hamiltonian_summary"]["integral_openfermion_bridge"].endswith("_v1")
    assert summary["hamiltonian_meta"]["n_active_orbitals"] == 1
    assert not summary["has_canonical_active_space_integral_pack"]


def test_pre_quantum_summary_includes_canonical_pack_provenance() -> None:
    compact = SimpleNamespace(
        n_active_orbitals=2,
        n_active_electrons=2,
        storage_schema="stub_compact_v1",
    )
    pack = CanonicalActiveSpaceIntegralPack(
        compact=compact,  # type: ignore[arg-type]
        provenance={
            "pack_schema": "qchem_canonical_active_space_integral_pack_v1",
            "upstream_integral_source": "stub_pack_v1",
            "classical_backend": "stub_backend",
        },
    )
    qh = QubitHamiltonian(
        operator=QubitOperator("Z0", 0.5),
        n_qubits=2,
        meta={
            "integral_source": "stub_pack_v1",
            "fermion_to_qubit_map": "bravyi_kitaev",
            "hamiltonian_fingerprint": "def456",
        },
    )
    pre_q = PreQuantumInput(
        classical_reference=_reference(),
        qubit_hamiltonian=qh,
        canonical_active_space_integral_pack=pack,
        meta=pre_quantum_meta_from_hamiltonian(
            source="canonical_active_space_integral_pack",
            qubit_hamiltonian=qh,
        ),
    )

    summary = pre_q.as_summary_dict()

    assert summary["has_canonical_active_space_integral_pack"]
    pack_summary = summary["canonical_active_space_integral_pack"]
    assert pack_summary["provenance"]["upstream_integral_source"] == "stub_pack_v1"
    assert pack_summary["n_active_orbitals"] == 2
    assert pack_summary["compact_storage_schema"] == "stub_compact_v1"

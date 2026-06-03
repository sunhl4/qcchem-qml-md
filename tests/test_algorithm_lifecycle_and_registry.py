from __future__ import annotations

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.protocols.computable import ExpectationValue, ExpectationValueDerivative
from qchem_stack.quantum.algorithm_registry import build_registered_algorithm
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.ansatz_registry import ansatz_registry_export
from qchem_stack.quantum.operator_pool_registry import (
    build_registered_operator_pool,
    list_registered_operator_pool_ids,
)


def _h2_toy_hamiltonian() -> QubitHamiltonian:
    h = (
        QubitOperator(((0, "Z"),), -0.7)
        + QubitOperator(((1, "Z"),), -0.7)
        + QubitOperator(((0, "X"), (1, "X")), 0.2)
    )
    return QubitHamiltonian(operator=h, n_qubits=2)


def test_vqe_lifecycle_report_with_gradient_expression() -> None:
    qh = _h2_toy_hamiltonian()
    exe = StatevectorHeaExecutor()
    objective = ExpectationValue(qh.operator, qh.n_qubits, 1, exe)
    gradient = ExpectationValueDerivative(objective, parameter_index=0)
    vqe = VQE(
        qh, depth=1, executor=exe, objective_expression=objective, gradient_expression=gradient
    )
    vqe.build()
    r = vqe.run(maxiter=10, seed=1)
    rep = vqe.generate_report()
    assert np.isfinite(r.energy)
    assert rep["schema"] == "algorithm_vqe_report_v1"
    assert "gradient_at_optimum" in rep
    assert isinstance(rep["final_parameters"], list)


def test_executable_registries_and_operator_pools() -> None:
    qh = _h2_toy_hamiltonian()
    algo = build_registered_algorithm("vqe", qh, depth=1)
    assert algo.__class__.__name__ == "VQE"
    assert "hea" in ansatz_registry_export()
    assert "fermionic_uccsd" in list_registered_operator_pool_ids()
    assert "fermionic_uccsd_singles" in list_registered_operator_pool_ids()
    assert "qubit_excitation" in list_registered_operator_pool_ids()
    assert "uccsd_jw" in list_registered_operator_pool_ids()
    pool = build_registered_operator_pool("toy_pair_xx", qh)
    assert len(pool) >= 1


def test_fermionic_uccsd_singles_pool_smaller_than_full_uccsd() -> None:
    """Singles-only pool is a strict subset (fewer JW operators) when doubles exist."""
    h = (
        QubitOperator(((0, "Z"),), -0.5)
        + QubitOperator(((1, "Z"),), -0.5)
        + QubitOperator(((2, "Z"),), -0.1)
        + QubitOperator(((3, "Z"),), -0.1)
    )
    fs = FermionSpace(n_spin_orbitals=4, n_electrons=2)
    qh = QubitHamiltonian(operator=h, n_qubits=4, fermion_space=fs)
    full_sd = build_registered_operator_pool("fermionic_uccsd", qh)
    singles_only = build_registered_operator_pool("fermionic_uccsd_singles", qh)
    assert len(singles_only) >= 1
    assert len(full_sd) > len(singles_only)


def test_fermionic_uccsd_doubles_slices_partition_full_pool() -> None:
    """Singles-only + doubles-only JW pools partition full UCCSD pool on a 4-spin-orbital, 2e space."""
    h = (
        QubitOperator(((0, "Z"),), -0.5)
        + QubitOperator(((1, "Z"),), -0.5)
        + QubitOperator(((2, "Z"),), -0.1)
        + QubitOperator(((3, "Z"),), -0.1)
    )
    fs = FermionSpace(n_spin_orbitals=4, n_electrons=2)
    qh = QubitHamiltonian(operator=h, n_qubits=4, fermion_space=fs)
    full_sd = build_registered_operator_pool("fermionic_uccsd", qh)
    singles_only = build_registered_operator_pool("fermionic_uccsd_singles", qh)
    doubles_only = build_registered_operator_pool("fermionic_uccsd_doubles_only", qh)
    assert len(doubles_only) >= 1
    assert len(full_sd) == len(singles_only) + len(doubles_only)


def test_operator_pool_aliases_match_canonical_pools() -> None:
    qh = _h2_toy_hamiltonian()
    assert build_registered_operator_pool("qubit_excitation", qh) == build_registered_operator_pool(
        "iqeb_qubit_excitation", qh
    )
    h = (
        QubitOperator(((0, "Z"),), -0.5)
        + QubitOperator(((1, "Z"),), -0.5)
        + QubitOperator(((2, "Z"),), -0.1)
        + QubitOperator(((3, "Z"),), -0.1)
    )
    fs = FermionSpace(n_spin_orbitals=4, n_electrons=2)
    qh2 = QubitHamiltonian(operator=h, n_qubits=4, fermion_space=fs)
    assert build_registered_operator_pool("uccsd_jw", qh2) == build_registered_operator_pool(
        "fermionic_uccsd", qh2
    )
    assert build_registered_operator_pool("uccsd_singles", qh2) == build_registered_operator_pool(
        "fermionic_uccsd_singles", qh2
    )
    assert build_registered_operator_pool(
        "uccsd_doubles_only", qh2
    ) == build_registered_operator_pool("fermionic_uccsd_doubles_only", qh2)
    assert build_registered_operator_pool(
        "uccsd_bk_singles", qh2
    ) == build_registered_operator_pool("fermionic_uccsd_singles_bravyi_kitaev", qh2)
    assert build_registered_operator_pool(
        "uccsd_bk_doubles_only", qh2
    ) == build_registered_operator_pool("fermionic_uccsd_doubles_bravyi_kitaev_only", qh2)
    assert build_registered_operator_pool(
        "uccsd_bk_singles_then_doubles", qh2
    ) == build_registered_operator_pool("fermionic_uccsd_singles_then_doubles_bk_concat", qh2)


def test_unknown_operator_pool_id_preserves_requested_label() -> None:
    qh = _h2_toy_hamiltonian()
    try:
        build_registered_operator_pool("not_a_real_pool", qh)
    except ValueError as e:
        assert "not_a_real_pool" in str(e)
    else:
        raise AssertionError("expected ValueError")

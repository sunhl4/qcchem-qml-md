from __future__ import annotations

import pytest

pytestmark = pytest.mark.l1_excited

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.protocols.protocol import PauliAveragingProtocol
from qchem_stack.quantum.algorithms.excited import QSE, VQD
from qchem_stack.quantum.algorithms.sceom import (
    default_sceom_pauli_generators,
    nested_sceom_q_sc_eom_operator,
    run_sceom_nested_commutator_from_hea,
)


def test_nested_sceom_operator_is_qubit_operator() -> None:
    h = QubitOperator(((0, "Z"),), 0.5) + QubitOperator((), 0.1)
    sx = QubitOperator(((0, "X"),), 1.0)
    op = nested_sceom_q_sc_eom_operator(h, sx, sx)
    assert len(op.terms) >= 1


def test_run_sceom_nested_from_hea() -> None:
    h = QubitOperator(((0, "Z"),), 0.4) + QubitOperator((), 0.05)
    qh = QubitHamiltonian(operator=h, n_qubits=1, fermion_space=FermionSpace(1, 1))
    res = run_sceom_nested_commutator_from_hea(qh, np.zeros(2), depth=1, subspace_dim=2)
    assert len(res.energies) == 2
    assert "D2SC05371C" in res.meta.get("reference", "")
    tasks = res.meta.get("sceom_m_element_tasks") or {}
    assert tasks.get("n_matrix_elements") == 4
    assert tasks.get("n_tasks_total") == 4


def test_run_sceom_nested_from_hea_grouped_shots() -> None:
    h = QubitOperator(((0, "Z"),), 0.4) + QubitOperator((), 0.05)
    qh = QubitHamiltonian(operator=h, n_qubits=1, fermion_space=FermionSpace(1, 1))
    res = run_sceom_nested_commutator_from_hea(
        qh, np.zeros(2), depth=1, subspace_dim=2, shots_per_matrix_element=128, seed=2
    )
    assert res.meta.get("shot_noise_model") == "grouped_statevector_shot_simulation_per_m_element"


def test_default_sceom_generators_count() -> None:
    ops = default_sceom_pauli_generators(3, 4)
    assert len(ops) == 4


def test_qse_pauli_transition_schedule_meta() -> None:
    h = QubitOperator(((0, "Z"),), 0.3) + QubitOperator(((1, "Z"),), 0.2) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=h, n_qubits=2, fermion_space=FermionSpace(2, 1))
    qse = QSE(qh, subspace_dim=4)
    r = qse.run_from_vqe_hea_basis_pauli_transitions(
        np.zeros(4), depth=1, max_basis=3, shots_per_ij_term=64, seed=1
    )
    assert r.meta.get("qse_pauli_transition_schedule", {}).get("n_transition_tasks", 0) > 0


def test_vqd_three_protocol_with_shots() -> None:
    op = QubitOperator(((0, "Z"),), 0.3) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    r = VQD(qh, n_states=2, depth=1).run(
        seed=0, shots_objective=200, shots_overlap=100, shots_weight=100
    )
    tp = r.meta["vqd_channels"][1]["three_protocol"]
    assert "objective" in tp and "overlap" in tp and "weight" in tp
    assert tp["objective"].get("energy_shot_mean") is not None


def test_vqd_three_computable_optimizer_mode() -> None:
    op = QubitOperator(((0, "Z"),), 0.3) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    r = VQD(qh, n_states=2, depth=1, optimizer_mode="three_computable").run(seed=0)
    assert r.meta.get("vqd_optimizer_mode") == "three_computable"
    trace = r.meta.get("vqd_optimizer_trace") or []
    assert len(trace) >= 1
    assert "three_protocol" in trace[0]
    assert trace[0].get("computable_runtime")


def test_vqd_deflation_circuit_overlap_mode_meta() -> None:
    op = QubitOperator(((0, "Z"),), 0.3) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    r = VQD(qh, n_states=2, depth=1, overlap_mode="deflation_circuit").run(seed=0)
    tda = r.meta.get("tangelo_deflation_analogy_v1") or {}
    assert tda.get("selected_overlap_mode") == "deflation_circuit"
    recipe = tda.get("deflation_circuit_recipe_v1") or {}
    assert isinstance(recipe, dict)
    sketch = recipe.get("circuit_ir_sketch_v1") or {}
    assert sketch.get("schema") == "vqd_deflation_swap_test_circuit_sketch_v1"
    assert any(str(op.get("name")) == "CSWAP" for op in (sketch.get("operations") or []))
    qiskit_ex = recipe.get("qiskit_export_v1") or {}
    assert qiskit_ex.get("schema") == "vqd_deflation_swap_test_qiskit_export_v1"
    assert qiskit_ex.get("twoq_gate_count", 0) >= 1


def test_pauli_protocol_records_histograms_when_requested() -> None:
    h = QubitOperator(((0, "Z"),), 1.0)
    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=200),
        pass_bundle=CompilerPassBundle(),
        run_sampled=True,
        record_histograms=True,
    )
    proto.build(np.array([0.1, 0.2, 0.3, 0.4]), hea_depth=1)
    proto.run()
    assert "measurement_histogram_rows" in proto._counts

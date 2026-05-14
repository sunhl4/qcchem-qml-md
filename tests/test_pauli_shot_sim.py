from __future__ import annotations

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.pauli_grouping import build_measurement_plan
from qchem_stack.backends.pauli_shot_sim import energy_estimate_grouped_shot_simulation
from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.protocols.protocol import PauliAveragingProtocol
from qchem_stack.quantum.statevector import expectation_qubit_operator, hea_state


def test_grouped_shot_simulation_mean_near_exact() -> None:
    h = (
        QubitOperator(((0, "Z"), (1, "Z")), 0.35)
        + QubitOperator(((0, "X"),), 0.08)
        + QubitOperator((), 0.12)
    )
    n_q = 2
    plan = build_measurement_plan(h, n_q, grouping="tensor_product")
    angles = np.array([0.2, -0.1, 0.3, 0.4])
    psi = hea_state(angles, n_q, 1)
    exact = float(np.real(expectation_qubit_operator(psi, h, n_q)))
    rng = np.random.default_rng(42)
    mean_e, stderr, meta = energy_estimate_grouped_shot_simulation(psi, h, plan, n_q, 25_000, rng)
    assert meta["total_shots_used"] > 0
    assert abs(mean_e - exact) < 0.08
    assert stderr >= 0.0


def test_protocol_run_sampled_sets_expectation_source() -> None:
    h = QubitOperator(((0, "Z"),), 0.5) + QubitOperator((), 0.1)
    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=BackendSpec(name="sim", shots_per_circuit=4000),
        pass_bundle=CompilerPassBundle(),
        run_sampled=True,
    )
    proto.build(np.array([0.1, 0.2, 0.3, 0.4]), hea_depth=1)
    proto.run()
    assert proto._counts["expectation_source"] == "grouped_shot_simulation_statevector"
    assert proto._counts["energy_stderr_model"] == "sample_stderr_independent_groups_approx"
    assert "shot_sim_meta" in proto._counts


def test_greedy_commuting_sampled_uses_one_joint_measurement_group() -> None:
    h = (
        QubitOperator(((0, "X"), (1, "X")), 0.31)
        + QubitOperator(((0, "Y"), (1, "Y")), -0.17)
        + QubitOperator(((0, "Z"), (1, "Z")), 0.23)
        + QubitOperator((), 0.05)
    )
    n_q = 2
    angles = np.array([0.2, -0.3, 0.4, 0.1])
    psi = hea_state(angles, n_q, 1)
    exact = float(np.real(expectation_qubit_operator(psi, h, n_q)))

    tensor_plan = build_measurement_plan(h, n_q, grouping="tensor_product")
    greedy_plan = build_measurement_plan(h, n_q, grouping="greedy_commuting")
    assert tensor_plan.n_circuits == 3
    assert greedy_plan.n_circuits == 1

    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=n_q,
        backend=BackendSpec(name="sim", shots_per_circuit=25_000),
        pass_bundle=CompilerPassBundle(),
        measurement_grouping="greedy_commuting",
        run_sampled=True,
        record_histograms=True,
    )
    proto.build(angles, hea_depth=1)
    proto.run(noise_rng=np.random.default_rng(7))

    assert len(proto._logical_circuits) == 1
    assert proto._logical_circuits[0].operations[-1]["name"] == "JOINT_PAULI_MEASURE"
    assert proto._counts["n_measurement_circuits"] == 1
    assert proto._counts["total_shots_budget"] == 25_000
    assert proto._counts["shot_sim_meta"]["shot_noise_model"] == "grouped_simultaneous_or_joint_projective"
    rows = proto._counts["measurement_histogram_rows"]
    assert rows[0]["mode"] == "commuting_joint_projective"
    assert abs(proto.evaluate() - exact) < 0.04

"""Pauli protocol RUN-stage expectation paths (exact / sampled / Qiskit shots)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.backends.shot_budget import energy_estimate_with_uncertainty
from qchem_stack.protocols.ansatz_prep import prepare_statevector
from qchem_stack.protocols.protocol_hea import hea_angles_for_depth

if TYPE_CHECKING:
    import numpy as np

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.backends.pauli_grouping import PauliMeasurementPlan
    from qchem_stack.protocols.protocol import PauliAveragingProtocol


def _base_counts(
    proto: PauliAveragingProtocol,
    *,
    expectation: float,
    expectation_source: str,
    energy_stderr_model: str,
    shots: int,
    stderr: float,
    plan: PauliMeasurementPlan,
    terms_dict: dict[Any, Any],
    n_groups: int,
    pmsv_stderr_scale: float,
    total_shots_budget: int,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    counts: dict[str, Any] = {
        "expectation": expectation,
        "expectation_source": expectation_source,
        "energy_stderr_model": energy_stderr_model,
        "raw_shots": proto.backend.shots_per_circuit,
        "shots_per_circuit_effective": shots,
        "energy_stderr": stderr,
        "n_measurement_circuits": plan.n_circuits,
        "total_shots_budget": total_shots_budget,
        "n_pauli_terms": len(terms_dict),
        "n_pauli_groups": n_groups,
        "pmsv_stderr_scale": pmsv_stderr_scale,
    }
    if extra:
        counts.update(extra)
    return counts


def _resolved_ansatz_prep(proto: PauliAveragingProtocol):
    from qchem_stack.protocols.ansatz_prep import AnsatzPrepSpec

    if proto.ansatz_prep is not None:
        return proto.ansatz_prep
    return AnsatzPrepSpec.hea(
        n_qubits=proto.n_qubits,
        angles=proto.angles,
        depth=int(proto.hea_depth),
    )


def run_sampled_shot_simulation(
    proto: PauliAveragingProtocol,
    *,
    plan: PauliMeasurementPlan,
    terms_dict: dict[Any, Any],
    shots: int,
    n_groups: int,
    pmsv_stderr_scale: float,
    noise_rng: np.random.Generator,
) -> dict[str, Any]:
    from qchem_stack.backends.pauli_shot_sim import energy_estimate_grouped_shot_simulation

    prep = _resolved_ansatz_prep(proto)
    psi = prepare_statevector(prep)
    e_sim, se_sim, sim_meta = energy_estimate_grouped_shot_simulation(
        psi,
        proto.hamiltonian,
        plan,
        proto.n_qubits,
        shots,
        noise_rng,
        return_histograms=proto.record_histograms,
    )
    counts = _base_counts(
        proto,
        expectation=float(e_sim),
        expectation_source="grouped_shot_simulation_statevector",
        energy_stderr_model="sample_stderr_independent_groups_approx",
        shots=shots,
        stderr=float(se_sim) * pmsv_stderr_scale,
        plan=plan,
        terms_dict=terms_dict,
        n_groups=n_groups,
        pmsv_stderr_scale=pmsv_stderr_scale,
        total_shots_budget=int(sim_meta.get("total_shots_used", shots * max(1, n_groups))),
        extra={"shot_sim_meta": sim_meta},
    )
    if proto.record_histograms and "measurement_histogram_rows" in sim_meta:
        counts["measurement_histogram_rows"] = sim_meta["measurement_histogram_rows"]
    return counts


def run_qiskit_shot_counts(
    proto: PauliAveragingProtocol,
    *,
    plan: PauliMeasurementPlan,
    terms_dict: dict[Any, Any],
    shots: int,
    n_groups: int,
    pmsv_stderr_scale: float,
    noise_rng: np.random.Generator,
) -> dict[str, Any]:
    from qchem_stack.backends.qiskit_pauli_shots import energy_estimate_grouped_qiskit_shots

    prep = _resolved_ansatz_prep(proto)
    e_q, se_q, q_meta = energy_estimate_grouped_qiskit_shots(
        proto.hamiltonian,
        plan,
        proto.n_qubits,
        proto.hea_depth,
        proto.angles,
        shots,
        proto.backend,
        noise_rng,
        return_histograms=proto.record_histograms,
        ansatz_prep=prep,
    )
    counts = _base_counts(
        proto,
        expectation=float(e_q),
        expectation_source="qiskit_shot_counts_get_counts",
        energy_stderr_model="empirical_shot_variance_independent_groups_approx",
        shots=shots,
        stderr=float(se_q) * pmsv_stderr_scale,
        plan=plan,
        terms_dict=terms_dict,
        n_groups=n_groups,
        pmsv_stderr_scale=pmsv_stderr_scale,
        total_shots_budget=int(q_meta.get("total_shots_used", shots * max(1, n_groups))),
        extra={"qiskit_pauli_shot_meta": q_meta},
    )
    if proto.record_histograms and "measurement_histogram_rows" in q_meta:
        counts["measurement_histogram_rows"] = q_meta["measurement_histogram_rows"]
    return counts


def run_exact_executor_expectation(
    proto: PauliAveragingProtocol,
    *,
    plan: PauliMeasurementPlan,
    terms_dict: dict[Any, Any],
    shots: int,
    n_groups: int,
    pmsv_stderr_scale: float,
    exe: HamiltonianExpectationExecutor,
) -> dict[str, Any]:
    prep = _resolved_ansatz_prep(proto)
    if prep.kind == "hea":
        e = exe.expectation_hea(
            proto.hamiltonian,
            proto.n_qubits,
            hea_angles_for_depth(
                proto.angles,
                n_qubits=proto.n_qubits,
                base_depth=int(proto.hea_depth),
                eff_depth=int(proto.hea_depth),
            ),
            proto.hea_depth,
        )
    else:
        psi = prepare_statevector(prep)
        e = exe.expectation_state(psi, proto.hamiltonian, proto.n_qubits)
    est = energy_estimate_with_uncertainty(e, plan, terms_dict, shots)
    return _base_counts(
        proto,
        expectation=e,
        expectation_source="executor_exact_or_device_mean",
        energy_stderr_model="conservative_sum_bound_equal_shots",
        shots=shots,
        stderr=float(est.stderr) * pmsv_stderr_scale,
        plan=plan,
        terms_dict=terms_dict,
        n_groups=n_groups,
        pmsv_stderr_scale=pmsv_stderr_scale,
        total_shots_budget=est.total_shots,
    )

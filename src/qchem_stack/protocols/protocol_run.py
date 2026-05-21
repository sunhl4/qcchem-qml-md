"""RUN stage orchestration for :class:`~qchem_stack.protocols.protocol.PauliAveragingProtocol`."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.backends.pauli_grouping import build_measurement_plan
from qchem_stack.backends.shot_budget import recommended_shots_per_circuit
from qchem_stack.protocols.protocol_phase import ProtocolPhase
from qchem_stack.protocols.protocol_run_mitigation import attach_pauli_support_and_mitigation
from qchem_stack.protocols.protocol_run_shot_modes import (
    run_exact_executor_expectation,
    run_qiskit_shot_counts,
    run_sampled_shot_simulation,
)

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.protocols.protocol import PauliAveragingProtocol


def run_energy_estimation(
    proto: PauliAveragingProtocol,
    noise_rng: np.random.Generator | None = None,
    executor: HamiltonianExpectationExecutor | None = None,
) -> None:
    """Populate ``proto._counts`` with expectation, stderr, and Pauli support metadata."""
    proto._phase = ProtocolPhase.RUN
    noise_rng = noise_rng or np.random.default_rng(0)
    exe = executor or proto.executor or executor_from_spec(proto.backend)
    plan = proto._measurement_plan or build_measurement_plan(
        proto.hamiltonian, proto.n_qubits, grouping=proto.measurement_grouping
    )
    proto._measurement_plan = plan
    terms_dict = dict(proto.hamiltonian.terms)
    tgt = proto.backend.target_energy_stderr
    shots = int(proto.backend.shots_per_circuit)
    if tgt is not None and float(tgt) > 0:
        shots = recommended_shots_per_circuit(plan, terms_dict, float(tgt))
    n_groups = len(plan.groups)
    pmsv_stderr_scale = 1.0
    if proto.pmsv is not None and 0.0 < float(proto.pmsv.retention_rate) < 1.0:
        pmsv_stderr_scale = 1.0 / math.sqrt(float(proto.pmsv.retention_rate))

    if proto.run_sampled and proto.run_qiskit_shots:
        raise ValueError(
            "run_sampled and run_qiskit_shots are mutually exclusive in PauliAveragingProtocol"
        )
    if proto.run_sampled:
        proto._counts = run_sampled_shot_simulation(
            proto,
            plan=plan,
            terms_dict=terms_dict,
            shots=shots,
            n_groups=n_groups,
            pmsv_stderr_scale=pmsv_stderr_scale,
            noise_rng=noise_rng,
        )
    elif proto.run_qiskit_shots:
        proto._counts = run_qiskit_shot_counts(
            proto,
            plan=plan,
            terms_dict=terms_dict,
            shots=shots,
            n_groups=n_groups,
            pmsv_stderr_scale=pmsv_stderr_scale,
            noise_rng=noise_rng,
        )
    else:
        proto._counts = run_exact_executor_expectation(
            proto,
            plan=plan,
            terms_dict=terms_dict,
            shots=shots,
            n_groups=n_groups,
            pmsv_stderr_scale=pmsv_stderr_scale,
            exe=exe,
        )

    attach_pauli_support_and_mitigation(proto, plan, shots, n_groups, noise_rng, exe)

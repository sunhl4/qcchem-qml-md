"""Build :class:`~qchem_stack.protocols.protocol.PauliAveragingProtocol` for pipeline / jobs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.config.quantum_helpers import (
    pauli_record_histograms,
    pauli_run_qiskit_shots,
    pauli_run_sampled,
    resolve_pauli_grouping,
    resolve_pauli_support_max_terms,
    resolve_uccsd_decomposition_mode,
    resolve_uccsd_trotter_steps,
    resolve_variational_ansatz,
)
from qchem_stack.mitigation.pmsv import PMSVConfig
from qchem_stack.protocols.ansatz_prep import AnsatzPrepSpec
from qchem_stack.protocols.protocol import PauliAveragingProtocol

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig


def ansatz_prep_for_job(
    cfg: ExperimentConfig,
    qh: QubitHamiltonian,
    angles: np.ndarray | list[float],
    *,
    hea_depth: int,
) -> AnsatzPrepSpec:
    ang = np.asarray(angles, dtype=float)
    if resolve_variational_ansatz(cfg) == "uccsd":
        return AnsatzPrepSpec.uccsd(
            hamiltonian=qh,
            angles=ang,
            trotter_steps=resolve_uccsd_trotter_steps(cfg),
            decomposition_mode=resolve_uccsd_decomposition_mode(cfg),  # type: ignore[arg-type]
        )
    return AnsatzPrepSpec.hea(n_qubits=qh.n_qubits, angles=ang, depth=int(hea_depth))


def protocol_for_job(
    cfg: ExperimentConfig,
    qh: QubitHamiltonian,
    *,
    bspec: BackendSpec,
    exe: HamiltonianExpectationExecutor,
    bundle: CompilerPassBundle,
) -> PauliAveragingProtocol:
    pmsv = None
    if cfg.mitigation.pmsv.enabled:
        pmsv = PMSVConfig(
            stabilizers=list(cfg.mitigation.pmsv.stabilizers),
            retention_rate=float(cfg.mitigation.pmsv.retention_rate),
            report_extension=str(cfg.mitigation.pmsv.report_extension),
            extra=dict(cfg.mitigation.pmsv.extra),
        )
    return PauliAveragingProtocol(
        hamiltonian=qh.operator,
        n_qubits=qh.n_qubits,
        backend=bspec,
        pass_bundle=bundle,
        pmsv=pmsv,
        zne_scales=[float(s) for s in cfg.mitigation.zne.scales]
        if cfg.mitigation.zne.enabled
        else None,
        zne_mode=cfg.mitigation.zne.mode,
        measurement_grouping=resolve_pauli_grouping(cfg),
        run_sampled=pauli_run_sampled(cfg),
        run_qiskit_shots=pauli_run_qiskit_shots(cfg),
        record_histograms=pauli_record_histograms(cfg),
        executor=exe,
        nexus_analog=cfg.nexus_analog,
        pauli_support_max_terms=resolve_pauli_support_max_terms(cfg),
    )

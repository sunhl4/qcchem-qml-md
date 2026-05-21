"""Build :class:`~qchem_stack.protocols.protocol.PauliAveragingProtocol` for pipeline / jobs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.mitigation.pmsv import PMSVConfig
from qchem_stack.protocols.protocol import PauliAveragingProtocol

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig


def protocol_for_job(
    cfg: ExperimentConfig,
    qh: QubitHamiltonian,
    *,
    bspec: Any,
    exe: Any,
    bundle: Any,
) -> PauliAveragingProtocol:
    q = cfg.quantum
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
        measurement_grouping=q.pauli.grouping,
        run_sampled=q.pauli.run_sampled,
        run_qiskit_shots=q.pauli.run_qiskit_shots,
        record_histograms=q.pauli.record_histograms,
        executor=exe,
        nexus_analog=cfg.nexus_analog,
        pauli_support_max_terms=q.pauli.support_max_terms,
    )

"""Read-only helpers for :class:`~qchem_stack.config.quantum.QuantumSpec`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .experiment import ExperimentConfig


def resolve_variational_algorithm(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.algorithm).strip()


def resolve_vqe_depth(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.vqe.depth)


def resolve_vqe_maxiter(cfg: ExperimentConfig) -> int:
    return int(cfg.quantum.vqe.maxiter)


def resolve_variational_ansatz(cfg: ExperimentConfig) -> str:
    return str(cfg.quantum.variational.ansatz)


def pauli_protocol_enabled(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.use_protocol)


def pauli_run_sampled(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.run_sampled)


def pauli_run_qiskit_shots(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.pauli.run_qiskit_shots)


def excited_vqd_after_variational(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.excited.vqd.after_variational)


def excited_qse_after_variational(cfg: ExperimentConfig) -> bool:
    return bool(cfg.quantum.excited.qse.after_variational)


def quantum_repro_core_fields(cfg: ExperimentConfig) -> dict[str, object]:
    """Stable repro snapshot keys derived from quantum + related config."""
    q = cfg.quantum
    out: dict[str, object] = {
        "quantum_algorithm": q.algorithm,
        "use_pauli_protocol": q.pauli.use_protocol,
        "vqe_depth": q.vqe.depth,
        "vqe_maxiter": q.vqe.maxiter,
        "adapt_max_iter": q.adapt.max_iter,
        "iqeb_max_rounds": q.iqeb.max_rounds,
        "variational_ansatz": q.variational.ansatz,
        "run_sampled_pauli_protocol": q.pauli.run_sampled,
        "run_qiskit_shots_pauli_protocol": q.pauli.run_qiskit_shots,
        "record_pauli_measurement_histograms": q.pauli.record_histograms,
        "pauli_grouping": q.pauli.grouping,
        "pauli_support_max_terms": q.pauli.support_max_terms,
        "vqd_after_variational": q.excited.vqd.after_variational,
        "qse_after_variational": q.excited.qse.after_variational,
    }
    if q.algorithm_factory:
        out["quantum_algorithm_factory"] = q.algorithm_factory
    if q.variational.ansatz == "uccsd" and q.variational.uccsd_trotter_steps is not None:
        out["uccsd_trotter_steps"] = q.variational.uccsd_trotter_steps
    return out

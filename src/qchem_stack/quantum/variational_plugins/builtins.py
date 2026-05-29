"""Built-in variational plug-ins (pipeline main line)."""

from __future__ import annotations

import numpy as np

from qchem_stack.config.quantum_helpers import (
    resolve_adapt_grad_tol,
    resolve_adapt_max_iter,
    resolve_adapt_pool_id,
    resolve_iqeb_energy_tolerance,
    resolve_iqeb_max_rounds,
    resolve_iqeb_n_grads,
    resolve_iqeb_pool_id,
    resolve_uccsd_trotter_steps,
    resolve_variational_algorithm,
    resolve_variational_ansatz,
    resolve_vqe_depth,
    resolve_vqe_initial_parameters_strategy,
    resolve_vqe_maxiter,
    resolve_vqe_optimizer_method,
    resolve_vsqs_intervals,
    resolve_vsqs_time,
    resolve_vsqs_trotter_order,
)
from qchem_stack.quantum.algorithms.adapt import FermionicAdaptVQE
from qchem_stack.quantum.algorithms.iqcc import IQCCVQE
from qchem_stack.quantum.algorithms.iqeb import IQEBVQE
from qchem_stack.quantum.algorithms.puccd_vqe import PUCCDVQE, puccd_algorithm_report_v1
from qchem_stack.quantum.algorithms.qcc_vqe import QCCVQE, qcc_algorithm_report_v1
from qchem_stack.quantum.algorithms.qite import QITEVQE
from qchem_stack.quantum.algorithms.qpe import (
    AlgorithmDeterministicQPE,
    AlgorithmInfoTheoryQPE,
    AlgorithmKitaevQPE,
)
from qchem_stack.quantum.algorithms.sa_vqe import SAVQE
from qchem_stack.quantum.algorithms.uccgd_vqe import UCCGDVQE, uccgd_algorithm_report_v1
from qchem_stack.quantum.algorithms.uccsd_vqe import uccsd_algorithm_report_v1
from qchem_stack.quantum.algorithms.upccgsd_vqe import UpCCGSDVQE, upccgsd_algorithm_report_v1
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.algorithms.vsqs_vqe import VSQSVQE, vsqs_algorithm_report_v1
from qchem_stack.quantum.variational_branch import run_uccsd_vqe_from_config
from qchem_stack.quantum.variational_plugins.spec import (
    VariationalRunContext,
    VariationalStageOutcome,
)


def _vqe_outcome(result: object, algorithm_report: object) -> VariationalStageOutcome:
    """Build the common ``VariationalStageOutcome`` shared by VQE-family ansätze.

    All standard runners report ``algorithm="vqe"`` with ``nfev`` / ``vqe_meta``
    drawn from the run result; only the attached ``algorithm_report`` differs.
    """
    return VariationalStageOutcome(
        energy=float(result.energy),  # type: ignore[attr-defined]
        angles=np.asarray(result.angles, dtype=float),  # type: ignore[attr-defined]
        algo_meta={
            "algorithm": "vqe",
            "nfev": result.nfev,  # type: ignore[attr-defined]
            "vqe_meta": result.meta,  # type: ignore[attr-defined]
        },
        algorithm_report=algorithm_report,
    )


# Ansätze whose runner is ``Class(qh, executor=exe).run(maxiter=, seed=)`` with a
# dedicated ``*_algorithm_report_v1`` builder and the standard outcome shape.
_STANDARD_VQE_ANSATZE: dict[str, tuple[type, object]] = {
    "uccgd": (UCCGDVQE, uccgd_algorithm_report_v1),
    "qcc": (QCCVQE, qcc_algorithm_report_v1),
    "upccgsd": (UpCCGSDVQE, upccgsd_algorithm_report_v1),
    "puccd": (PUCCDVQE, puccd_algorithm_report_v1),
}


def run_vqe_branch(ctx: VariationalRunContext) -> VariationalStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    exe = ctx.executor
    ansatz = resolve_variational_ansatz(cfg)

    if ansatz == "uccsd":
        ur = run_uccsd_vqe_from_config(
            qh,
            exe,
            maxiter=resolve_vqe_maxiter(cfg),
            seed=ctx.seed,
            trotter_steps=resolve_uccsd_trotter_steps(cfg),
        )
        return _vqe_outcome(ur, uccsd_algorithm_report_v1(ur))

    standard = _STANDARD_VQE_ANSATZE.get(ansatz)
    if standard is not None:
        cls, report_fn = standard
        result = cls(qh, executor=exe).run(maxiter=resolve_vqe_maxiter(cfg), seed=ctx.seed)
        return _vqe_outcome(result, report_fn(result))  # type: ignore[operator]

    if ansatz == "iqcc":
        ir = IQCCVQE(qh, executor=exe).run(maxiter=resolve_vqe_maxiter(cfg), seed=ctx.seed)
        return _vqe_outcome(
            ir,
            {
                "schema": "algorithm_iqcc_report_v1",
                "algorithm": "vqe",
                "variational_ansatz": "iqcc",
                "final_value": float(ir.energy),
                "nfev": int(ir.nfev),
                "meta": dict(ir.meta),
            },
        )
    if ansatz == "qite":
        qr = QITEVQE(qh, executor=exe).run(seed=ctx.seed)
        return VariationalStageOutcome(
            energy=float(qr.energy),
            angles=np.asarray(qr.angles, dtype=float),
            algo_meta={"algorithm": "vqe", "nfev": qr.n_steps, "vqe_meta": qr.meta},
            algorithm_report={
                "schema": "algorithm_qite_report_v1",
                "algorithm": "vqe",
                "variational_ansatz": "qite",
                "final_value": float(qr.energy),
                "n_steps": int(qr.n_steps),
                "meta": dict(qr.meta),
            },
        )
    if ansatz == "vsqs":
        vr = VSQSVQE(
            qh,
            intervals=resolve_vsqs_intervals(cfg),
            time=resolve_vsqs_time(cfg),
            trotter_order=resolve_vsqs_trotter_order(cfg),
            executor=exe,
        ).run(maxiter=resolve_vqe_maxiter(cfg), seed=ctx.seed)
        return _vqe_outcome(vr, vsqs_algorithm_report_v1(vr))

    depth = resolve_vqe_depth(cfg)
    init = (
        np.zeros(2 * qh.n_qubits * depth, dtype=float)
        if resolve_vqe_initial_parameters_strategy(cfg) == "zeros"
        else None
    )
    vqe = VQE(
        qh,
        depth=depth,
        executor=exe,
        optimizer_method=resolve_vqe_optimizer_method(cfg),
    )
    vr = vqe.run(
        maxiter=resolve_vqe_maxiter(cfg),
        initial_parameters=init,
        seed=ctx.seed,
    )
    return _vqe_outcome(vr, vqe.generate_report())


def run_adapt_family(ctx: VariationalRunContext) -> VariationalStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    av = FermionicAdaptVQE(
        qh,
        max_ops=resolve_adapt_max_iter(cfg),
        hea_depth=resolve_vqe_depth(cfg),
        pool_id=resolve_adapt_pool_id(cfg),
        tetris_style=(resolve_variational_algorithm(cfg) == "tetris_adapt"),
        executor=ctx.executor,
    )
    grad_tol = resolve_adapt_grad_tol(cfg)
    ar = av.run(grad_tol=grad_tol, seed=ctx.seed)
    hea_angles = np.asarray(ar.meta["hea_angles"], dtype=float)
    return VariationalStageOutcome(
        energy=float(ar.energy),
        angles=hea_angles,
        algo_meta={
            "algorithm": resolve_variational_algorithm(cfg),
            "adapt_meta": ar.meta,
            "adapt_pool": ar.pool_indices,
        },
        algorithm_report=av.generate_report(),
    )


def run_iqeb(ctx: VariationalRunContext) -> VariationalStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    iq = IQEBVQE(
        qh,
        max_rounds=resolve_iqeb_max_rounds(cfg),
        n_grads=resolve_iqeb_n_grads(cfg),
        energy_tolerance=resolve_iqeb_energy_tolerance(cfg),
        pool_id=resolve_iqeb_pool_id(cfg),
        executor=ctx.executor,
    )
    ir = iq.run(depth=resolve_vqe_depth(cfg), seed=ctx.seed)
    return VariationalStageOutcome(
        energy=float(ir.energy),
        angles=np.asarray(ir.vqe.angles, dtype=float),
        algo_meta={
            "algorithm": "iqeb",
            "iqeb_meta": ir.meta,
            "iqeb_selected_pauli_strings": ir.selected_pauli_strings,
            "nfev": ir.vqe.nfev,
            "vqe_meta": ir.vqe.meta,
        },
        algorithm_report=iq.generate_report(),
    )


def _qpe_stage_outcome(
    ctx: VariationalRunContext,
    *,
    algorithm_label: str,
    qpe: AlgorithmKitaevQPE | AlgorithmDeterministicQPE | AlgorithmInfoTheoryQPE,
    run_kwargs: dict[str, object] | None = None,
) -> VariationalStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    depth = resolve_vqe_depth(cfg)
    angles = np.zeros(2 * qh.n_qubits * depth, dtype=float)
    kr = qpe.build().run(**(run_kwargs or {}))  # type: ignore[attr-defined]
    report = qpe.generate_report()
    return VariationalStageOutcome(
        energy=float(kr.energy_estimate),
        angles=angles,
        algo_meta={
            "algorithm": algorithm_label,
            f"{algorithm_label}_meta": dict(kr.meta),
            "phase_mu": float(kr.phase_mu),
            "phase_sigma": float(kr.phase_sigma),
        },
        algorithm_report=report if isinstance(report, dict) else None,
    )


def run_qpe_kitaev(ctx: VariationalRunContext) -> VariationalStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    qt = cfg.quantum
    t_ev = float(qt.demos.qpe.three_pack.time)
    n_bits = int(qt.demos.qpe.three_pack.kitaev_bits)
    kit = AlgorithmKitaevQPE(qh, time=t_ev, n_bits=n_bits)
    return _qpe_stage_outcome(ctx, algorithm_label="qpe_kitaev", qpe=kit)


def run_qpe_deterministic(ctx: VariationalRunContext) -> VariationalStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    qt = cfg.quantum
    t_ev = float(qt.demos.qpe.three_pack.time)
    n_rounds = int(qt.demos.qpe.three_pack.deterministic_rounds)
    det = AlgorithmDeterministicQPE(qh, time=t_ev, n_rounds=n_rounds)
    return _qpe_stage_outcome(ctx, algorithm_label="qpe_deterministic", qpe=det)


def run_qpe_info_theory(ctx: VariationalRunContext) -> VariationalStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    qt = cfg.quantum
    t_ev = float(qt.demos.qpe.three_pack.time)
    n_samples = int(qt.demos.qpe.three_pack.info_samples)
    info = AlgorithmInfoTheoryQPE(qh, time=t_ev, n_samples=n_samples)
    return _qpe_stage_outcome(
        ctx,
        algorithm_label="qpe_info_theory",
        qpe=info,
        run_kwargs={"seed": ctx.seed},
    )


def run_sa_vqe_branch(ctx: VariationalRunContext) -> VariationalStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    exe = ctx.executor
    depth = resolve_vqe_depth(cfg)
    sa = SAVQE(qh, depth=depth, executor=exe)
    sr = sa.run(maxiter=resolve_vqe_maxiter(cfg), seed=ctx.seed)
    return VariationalStageOutcome(
        energy=float(sr.energy),
        angles=np.asarray(sr.angles, dtype=float),
        algo_meta={"algorithm": "sa_vqe", "nfev": sr.nfev, "sa_vqe_meta": sr.meta},
        algorithm_report={"schema": "algorithm_sa_vqe_report_v1", "final_value": sr.energy},
    )


BUILTIN_RUNNERS: dict[str, object] = {
    "vqe": run_vqe_branch,
    "adapt": run_adapt_family,
    "tetris_adapt": run_adapt_family,
    "iqeb": run_iqeb,
    "sa_vqe": run_sa_vqe_branch,
    "qpe_kitaev": run_qpe_kitaev,
    "qpe_deterministic": run_qpe_deterministic,
    "qpe_info_theory": run_qpe_info_theory,
}

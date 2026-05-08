"""Built-in variational plug-ins (pipeline main line)."""

from __future__ import annotations

import numpy as np

from qchem_stack.quantum.algorithms.adapt import FermionicAdaptVQE
from qchem_stack.quantum.algorithms.iqeb import IQEBVQE
from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.variational_plugins.spec import (
    VariationalRunContext,
    VariationalStageOutcome,
)


def run_vqe_branch(ctx: VariationalRunContext) -> VariationalStageOutcome:
    q = ctx.cfg.quantum
    qh = ctx.hamiltonian
    exe = ctx.executor
    if q.variational_ansatz == "uccsd":
        if q.uccsd_trotter_steps is not None:
            ur = UCCSDTrotterVQE(
                qh,
                executor=exe,
                n_trotter_steps=int(q.uccsd_trotter_steps),
            ).run(maxiter=q.vqe_maxiter, seed=ctx.seed)
        else:
            ur = UCCSDVQE(qh, executor=exe).run(maxiter=q.vqe_maxiter, seed=ctx.seed)
        return VariationalStageOutcome(
            energy=float(ur.energy),
            angles=np.asarray(ur.angles, dtype=float),
            algo_meta={"algorithm": "vqe", "nfev": ur.nfev, "vqe_meta": ur.meta},
        )

    init = (
        np.zeros(2 * qh.n_qubits * q.vqe_depth, dtype=float)
        if q.vqe_initial_parameters_strategy == "zeros"
        else None
    )
    vr = VQE(
        qh,
        depth=q.vqe_depth,
        executor=exe,
        optimizer_method=q.vqe_optimizer_method,
    ).run(
        maxiter=q.vqe_maxiter,
        initial_parameters=init,
        seed=ctx.seed,
    )
    return VariationalStageOutcome(
        energy=float(vr.energy),
        angles=np.asarray(vr.angles, dtype=float),
        algo_meta={"algorithm": "vqe", "nfev": vr.nfev, "vqe_meta": vr.meta},
    )


def run_adapt_family(ctx: VariationalRunContext) -> VariationalStageOutcome:
    q = ctx.cfg.quantum
    av = FermionicAdaptVQE(
        ctx.hamiltonian,
        max_ops=q.adapt_max_iter,
        hea_depth=q.vqe_depth,
        pool_id=q.adapt_pool_id,
        tetris_style=(q.algorithm == "tetris_adapt"),
        executor=ctx.executor,
    )
    ar = av.run(seed=ctx.seed)
    hea_angles = np.asarray(ar.meta["hea_angles"], dtype=float)
    return VariationalStageOutcome(
        energy=float(ar.energy),
        angles=hea_angles,
        algo_meta={
            "algorithm": q.algorithm,
            "adapt_meta": ar.meta,
            "adapt_pool": ar.pool_indices,
        },
    )


def run_iqeb(ctx: VariationalRunContext) -> VariationalStageOutcome:
    q = ctx.cfg.quantum
    iq = IQEBVQE(
        ctx.hamiltonian,
        max_rounds=q.iqeb_max_rounds,
        n_grads=q.iqeb_n_grads,
        energy_tolerance=q.iqeb_energy_tolerance,
        pool_id=q.iqeb_pool_id,
        executor=ctx.executor,
    )
    ir = iq.run(depth=q.vqe_depth, seed=ctx.seed)
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
    )


BUILTIN_RUNNERS: dict[str, object] = {
    "vqe": run_vqe_branch,
    "adapt": run_adapt_family,
    "tetris_adapt": run_adapt_family,
    "iqeb": run_iqeb,
}

"""Built-in variational plug-ins (pipeline main line)."""

from __future__ import annotations

import numpy as np

from qchem_stack.config.quantum_helpers import (
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
)
from qchem_stack.quantum.algorithms.adapt import FermionicAdaptVQE
from qchem_stack.quantum.algorithms.iqeb import IQEBVQE
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.variational_branch import run_uccsd_vqe_from_config
from qchem_stack.quantum.variational_plugins.spec import (
    VariationalRunContext,
    VariationalStageOutcome,
)


def run_vqe_branch(ctx: VariationalRunContext) -> VariationalStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    exe = ctx.executor
    if resolve_variational_ansatz(cfg) == "uccsd":
        ur = run_uccsd_vqe_from_config(
            qh,
            exe,
            maxiter=resolve_vqe_maxiter(cfg),
            seed=ctx.seed,
            trotter_steps=resolve_uccsd_trotter_steps(cfg),
        )
        return VariationalStageOutcome(
            energy=float(ur.energy),
            angles=np.asarray(ur.angles, dtype=float),
            algo_meta={"algorithm": "vqe", "nfev": ur.nfev, "vqe_meta": ur.meta},
        )

    depth = resolve_vqe_depth(cfg)
    init = (
        np.zeros(2 * qh.n_qubits * depth, dtype=float)
        if resolve_vqe_initial_parameters_strategy(cfg) == "zeros"
        else None
    )
    vr = VQE(
        qh,
        depth=depth,
        executor=exe,
        optimizer_method=resolve_vqe_optimizer_method(cfg),
    ).run(
        maxiter=resolve_vqe_maxiter(cfg),
        initial_parameters=init,
        seed=ctx.seed,
    )
    return VariationalStageOutcome(
        energy=float(vr.energy),
        angles=np.asarray(vr.angles, dtype=float),
        algo_meta={"algorithm": "vqe", "nfev": vr.nfev, "vqe_meta": vr.meta},
    )


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
    ar = av.run(seed=ctx.seed)
    hea_angles = np.asarray(ar.meta["hea_angles"], dtype=float)
    return VariationalStageOutcome(
        energy=float(ar.energy),
        angles=hea_angles,
        algo_meta={
            "algorithm": resolve_variational_algorithm(cfg),
            "adapt_meta": ar.meta,
            "adapt_pool": ar.pool_indices,
        },
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
    )


BUILTIN_RUNNERS: dict[str, object] = {
    "vqe": run_vqe_branch,
    "adapt": run_adapt_family,
    "tetris_adapt": run_adapt_family,
    "iqeb": run_iqeb,
}

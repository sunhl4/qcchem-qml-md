"""Tiny VQE demonstration plug-in using the built-in :class:`~qchem_stack.quantum.algorithms.vqe.VQE`.

YAML: ``quantum.algorithm_factory: qchem_stack.quantum.variational_plugins.examples.vqe_micro_plugin:micro_vqe_runner_factory``

This differs from ``echo_runner`` which never calls the optimizer; here ``maxiter`` is clipped to demonstrate
factories composing core algorithms.
"""

from __future__ import annotations

import numpy as np

from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.variational_plugins.spec import (
    VariationalRunContext,
    VariationalStageOutcome,
)


def run_micro_vqe(ctx: VariationalRunContext) -> VariationalStageOutcome:
    qh = ctx.resolved_hamiltonian()
    q = ctx.cfg.quantum
    capped = max(1, min(int(q.vqe_maxiter), 8))
    vr = VQE(
        qh,
        depth=int(q.vqe_depth),
        executor=ctx.executor,
        optimizer_method=q.vqe_optimizer_method,
    ).run(maxiter=capped, seed=int(ctx.seed))
    return VariationalStageOutcome(
        energy=float(vr.energy),
        angles=np.asarray(vr.angles, dtype=float),
        algo_meta={
            "algorithm": q.algorithm,
            "nfev": int(vr.nfev),
            "variational_demo_plugin": "micro_vqe",
            "capped_maxiter_ran": capped,
            "vqe_meta": vr.meta,
        },
    )


def micro_vqe_runner_factory():
    """``quantum.algorithm_factory`` callable for loader registration."""

    return run_micro_vqe

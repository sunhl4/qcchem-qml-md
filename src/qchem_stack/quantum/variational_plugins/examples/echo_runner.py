"""Minimal reference plug-in: HEA expectation at θ=0 via the configured executor."""

from __future__ import annotations

import numpy as np

from qchem_stack.quantum.variational_plugins.spec import (
    VariationalRunContext,
    VariationalStageOutcome,
)


def run_echo_variational(ctx: VariationalRunContext) -> VariationalStageOutcome:
    qh = ctx.hamiltonian
    depth = int(ctx.cfg.quantum.vqe_depth)
    angles = np.zeros(2 * qh.n_qubits * depth, dtype=float)
    energy = float(ctx.executor.expectation_hea(qh.operator, qh.n_qubits, angles, depth))
    return VariationalStageOutcome(
        energy=energy,
        angles=angles,
        algo_meta={"algorithm": ctx.cfg.quantum.algorithm, "nfev": 0, "variational_echo_plugin": True},
    )


def echo_runner_factory():
    """YAML ``quantum.algorithm_factory: ...echo_runner:echo_runner_factory``."""

    return run_echo_variational

"""VQD optimizer and ground-state preparation helpers (split from facade)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import numpy as np
from scipy.optimize import minimize

from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.statevector import hea_state

from .excited_basis import vqd_cross_stack_semantics_meta

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.quantum.algorithms.excited_vqd import VQD


def pick_vqd_x0(
    vqd: VQD,
    *,
    level: int,
    n_param: int,
    reused_ground: bool,
    v0_angles: np.ndarray,
    x_prev: np.ndarray | None,
    rng: np.random.Generator,
) -> np.ndarray:
    strat = vqd.init_strategy
    if strat == "legacy":
        if level == 1 and reused_ground and len(v0_angles) == n_param:
            return cast("np.ndarray", np.asarray(v0_angles, dtype=float).copy())
        return rng.uniform(-np.pi, np.pi, size=n_param)
    if strat == "random_uniform":
        return rng.uniform(-np.pi, np.pi, size=n_param)
    if (
        strat == "reuse_ground_perturb"
        and level == 1
        and reused_ground
        and len(v0_angles) == n_param
    ):
        return cast(
            "np.ndarray",
            np.asarray(v0_angles, dtype=float)
            + rng.normal(0.0, vqd.init_noise_scale, size=n_param),
        )
    if (
        strat == "previous_layer_perturb"
        and level > 1
        and x_prev is not None
        and len(x_prev) == n_param
    ):
        return cast(
            "np.ndarray",
            np.asarray(x_prev, dtype=float) + rng.normal(0.0, vqd.init_noise_scale, size=n_param),
        )
    return rng.uniform(-np.pi, np.pi, size=n_param)


def minimize_vqd_objective(vqd: VQD, objective: Callable[[np.ndarray], float], x0: np.ndarray):
    mi = vqd.cobyla_maxiter
    m = vqd.optimizer_method
    if m == "COBYLA":
        return minimize(objective, x0, method="COBYLA", options={"maxiter": mi})
    if m == "NELDER-MEAD":
        return minimize(objective, x0, method="Nelder-Mead", options={"maxiter": max(mi, 200)})
    if m == "L-BFGS-B":
        bounds = vqd.parameter_bounds
        if bounds is None:
            bounds = [(-4.0 * np.pi, 4.0 * np.pi)] * len(x0)
        return minimize(objective, x0, method="L-BFGS-B", bounds=bounds, options={"maxiter": mi})
    raise ValueError(
        f"Unsupported VQD optimizer_method={vqd.optimizer_method!r} "
        "(use COBYLA, L-BFGS-B, Nelder-Mead)."
    )


def prepare_vqd_ground_level(
    vqd: VQD,
    *,
    exe: HamiltonianExpectationExecutor,
    seed: int,
    reused_ground: bool,
    ground_angles: np.ndarray | None,
    ground_energy: float | None,
    n_param: int,
) -> tuple[np.ndarray, list[float], np.ndarray]:
    if vqd.prepare_state is not None and not reused_ground:
        raise ValueError(
            "VQD with a custom prepare_state (e.g. UCCSD) requires ground_angles from the "
            "prior variational stage."
        )
    if reused_ground:
        ga = np.asarray(ground_angles, dtype=float).ravel()
        if ga.size != n_param:
            raise ValueError(
                f"ground_angles length {ga.size} != expected variational parameters {n_param}"
            )
        g0 = vqd._prep(ga)
        e0 = (
            float(ground_energy)
            if ground_energy is not None
            else float(
                exe.expectation_state(g0, vqd.hamiltonian.operator, vqd.hamiltonian.n_qubits)
            )
        )
        return g0, [e0], ga
    v0 = VQE(vqd.hamiltonian, depth=vqd.depth, executor=exe).run(seed=seed)
    g0 = hea_state(v0.angles, vqd.hamiltonian.n_qubits, vqd.depth)
    return g0, [v0.energy], np.asarray(v0.angles, dtype=float)


def build_vqd_excited_result_meta(
    vqd: VQD,
    *,
    penalties: list[float],
    vqd_channels: list[dict[str, Any]],
    opt_trace: list[dict[str, Any]],
    warnings: list[str],
    reused_ground: bool,
    shots_objective: int,
    shots_overlap: int,
    shots_weight: int,
) -> dict[str, Any]:
    result_meta: dict[str, Any] = {
        "orthogonal_weight": vqd.penalty_weight,
        "vqd_penalty_weights_resolved": penalties,
        "reference": "Quantum 3, 156 (2019)",
        "vqd_channels": vqd_channels,
        "implementation_note": "three_protocol_reporting_objective_overlap_weight",
        "shots_objective": shots_objective,
        "shots_overlap": shots_overlap,
        "shots_weight": shots_weight,
        "reused_pipeline_ground": reused_ground,
        "overlap_exponent_yaml": float(vqd.overlap_exponent),
        "cobyla_maxiter_yaml": int(vqd.cobyla_maxiter),
        "vqd_optimizer_method": vqd.optimizer_method,
        "vqd_optimizer_mode": vqd.optimizer_mode,
        "vqd_optimizer_trace": opt_trace if vqd.optimizer_mode == "three_computable" else [],
        "vqd_init_strategy_yaml": vqd.init_strategy,
        "vqd_init_noise_scale_yaml": float(vqd.init_noise_scale),
        "vqd_overlap_mode_yaml": vqd.overlap_mode,
        "vqd_variety_yaml": "uccsd" if vqd.prepare_state else "hea",
    }
    if warnings:
        result_meta["vqd_warnings"] = warnings
    result_meta.update(
        vqd_cross_stack_semantics_meta(
            penalty_weight=vqd.penalty_weight,
            penalty_weights_resolved=penalties,
            overlap_mode=vqd.overlap_mode,
            optimizer_mode=vqd.optimizer_mode,
            n_system_qubits=int(vqd.hamiltonian.n_qubits),
        )
    )
    return result_meta


__all__ = [
    "build_vqd_excited_result_meta",
    "minimize_vqd_objective",
    "pick_vqd_x0",
    "prepare_vqd_ground_level",
]

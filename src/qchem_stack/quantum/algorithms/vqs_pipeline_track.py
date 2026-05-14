"""Pipeline-facing VQS / McLachlan dynamics after variational (Methods narrative).

Supports either the historical **linear damping** toy flow (:class:`~AlgorithmVQS`) or a
finite-difference **HEA tangent-space McLachlan/TDVP Euler stepper** configured via
``quantum.vqs_rhs_mode`` *(ignored for bare ``quantum.vqs_mode: vqs`` — always damping)*.

This remains an open-stack analogue of vendor time-evolved variational workflows, not ion-trap parity.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.vqs import (
    AlgorithmMcLachlanImagTime,
    AlgorithmMcLachlanRealTime,
    AlgorithmVQS,
    RhsMode,
)


def _normalized_mode(mode: str) -> str:
    return str(mode).strip().lower().replace("-", "_")


def _effective_rhs_mode(yaml_track_mode: str, yaml_rhs: str) -> RhsMode:
    m = _normalized_mode(yaml_track_mode)
    if m in {"vqs", "algorithm_vqs"}:
        return "linear_damping"
    rhs = str(yaml_rhs).strip().lower().replace("-", "_")
    if rhs not in {"linear_damping", "hea_mclachlan_tdvp"}:
        raise ValueError(f"Unknown quantum.vqs_rhs_mode={yaml_rhs!r}")
    return rhs  # type: ignore[return-value]


def _select_runner(
    mode: str,
    qh: QubitHamiltonian,
    theta: np.ndarray,
    times: np.ndarray,
    *,
    rhs_mode: RhsMode,
    tangent_eps: float,
) -> AlgorithmVQS | AlgorithmMcLachlanRealTime | AlgorithmMcLachlanImagTime:
    m = _normalized_mode(mode)
    if m in {"vqs", "algorithm_vqs"}:
        return AlgorithmVQS(qh, theta, times, rhs_mode=rhs_mode, tangent_fd_epsilon=tangent_eps)
    if m in {"mclachlan_real_time", "mclachlanrealtime", "real"}:
        return AlgorithmMcLachlanRealTime(
            qh, theta, times, rhs_mode=rhs_mode, tangent_fd_epsilon=tangent_eps
        )
    if m in {"mclachlan_imag_time", "mclachlanimagtime", "imag"}:
        return AlgorithmMcLachlanImagTime(
            qh, theta, times, rhs_mode=rhs_mode, tangent_fd_epsilon=tangent_eps
        )
    raise ValueError(
        f"Unknown vqs_mode={mode!r}. "
        "Use 'vqs', 'mclachlan_real_time', or 'mclachlan_imag_time' (quantum.vqs_mode)."
    )


def vqs_track_payload(
    qh: QubitHamiltonian,
    angles: np.ndarray | list[float],
    *,
    mode: str,
    n_times: int,
    dt: float,
    rhs_mode_yaml: str = "linear_damping",
    tangent_fd_epsilon_yaml: float = 5e-5,
) -> dict[str, Any]:
    theta = np.asarray(angles, dtype=float).reshape(-1)
    if theta.size == 0:
        raise ValueError("vqs_track requires non-empty variational angles from the pipeline.")
    nt = int(n_times)
    if nt < 2:
        raise ValueError("vqs_n_times must be >= 2.")
    step = float(dt)
    times = np.linspace(0.0, step * float(nt - 1), num=nt, dtype=float)
    eff_rhs = _effective_rhs_mode(mode, rhs_mode_yaml)
    algo = _select_runner(
        mode, qh, theta, times, rhs_mode=eff_rhs, tangent_eps=float(tangent_fd_epsilon_yaml)
    )
    _ = algo.build()
    res = algo.run()

    traj = res.trajectory
    if eff_rhs == "linear_damping":
        contract_rhs = (
            "linear_damping_lambda_theta (λ=0.1) forward Euler "
            "(default when quantum.vqs_mode=='vqs' or rhs_mode_yaml requests damping)."
        )
        integrator = "forward_euler_linear_damping"
    else:
        contract_rhs = (
            "hea_mclachlan_tdvp: centred finite differences on HEA tangent directions + tangent linear solve; "
            "open-stack McLachlan analogue."
        )
        integrator = "forward_euler_tdvp_fd"

    return {
        "schema": "vqs_track_v1",
        "epistemic_bound": (
            "Open-stack variational-parameter dynamics analogue: damping toy or tangent-space Euler; "
            "not calibrated closed-source chemistry time-evolution parity."
        ),
        "vqs_integration_contract_v1": {
            "schema": "vqs_integration_contract_v1",
            "rhs_model_effective": eff_rhs,
            "rhs_yaml_requested": rhs_mode_yaml,
            "rhs_descriptor": contract_rhs,
            "tangent_finite_difference_epsilon_yaml": float(tangent_fd_epsilon_yaml),
            "integrator": integrator,
            "modes_supported": ["vqs", "mclachlan_real_time", "mclachlan_imag_time"],
        },
        "vqs_mode": str(mode),
        "times": [float(t) for t in res.times],
        "n_steps": int(res.meta.get("n_steps", len(res.times) - 1)),
        "initial_parameters": [float(x) for x in traj[0]],
        "final_parameters": [float(x) for x in traj[-1]],
        "energy_observable": [float(x) for x in res.observables.get("energy", [])],
        "algorithm_report": algo.generate_report(),
    }

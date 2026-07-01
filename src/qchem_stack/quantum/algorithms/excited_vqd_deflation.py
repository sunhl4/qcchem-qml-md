"""Sequential VQD deflation loop and three-protocol channel reporting."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import numpy as np

from qchem_stack.quantum.algorithms.excited_basis import (
    _vqd_objective_computable,
    _vqd_overlap_computable,
    _vqd_three_protocol_channels,
    _vqd_weight_computable,
    vqd_cross_stack_semantics_meta,
)
from qchem_stack.quantum.algorithms.excited_vqd_types import VQDResult
from qchem_stack.quantum.algorithms.tolerances import FLOAT_PRECISION_TINY

if TYPE_CHECKING:
    from scipy.optimize import OptimizeResult

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.quantum.algorithms.excited_vqd import VQD


def run_vqd_deflation(
    vqd: VQD,
    *,
    exe: HamiltonianExpectationExecutor,
    seed: int,
    shots_objective: int,
    shots_overlap: int,
    shots_weight: int,
    pauli_grouping: str,
    ground_angles: np.ndarray | None,
    ground_energy: float | None,
) -> VQDResult:
    """Run multi-state VQD deflation (level 0 + excited levels)."""
    rng = np.random.default_rng(seed + 1)
    n_param = vqd._n_params()
    penalties = vqd._resolve_penalties()
    reused_ground = ground_angles is not None

    g0, energies, v0_angles = vqd._prepare_ground_level(
        exe=exe,
        seed=seed,
        reused_ground=reused_ground,
        ground_angles=ground_angles,
        ground_energy=ground_energy,
        n_param=n_param,
    )

    if vqd.n_states < 2:
        meta = {
            "reference": "Quantum 3, 156 (2019) — collapsed single-objective deflation",
            "reused_pipeline_ground": reused_ground,
            "vqd_variety_yaml": "uccsd" if vqd.prepare_state else "hea",
        }
        meta.update(
            vqd_cross_stack_semantics_meta(
                penalty_weight=vqd.penalty_weight,
                penalty_weights_resolved=[],
                overlap_mode=vqd.overlap_mode,
            )
        )
        return VQDResult(energies=energies, meta=meta)

    lam0 = penalties[0] if penalties else vqd.penalty_weight
    prev_states: list[np.ndarray] = [g0 / (np.linalg.norm(g0) + FLOAT_PRECISION_TINY)]
    g0n = prev_states[0]
    vqd_channels: list[dict[str, Any]] = [
        {
            "level": 0,
            "energy_exact": float(energies[0]),
            "overlap_squared_sum": 0.0,
            "channel_note": "ground_VQE_only",
            "three_protocol": _vqd_three_protocol_channels(
                [],
                g0n,
                vqd.hamiltonian.operator,
                vqd.hamiltonian.n_qubits,
                lam0,
                shots_objective=shots_objective,
                shots_overlap=0,
                shots_weight=0,
                rng=rng,
                pauli_grouping=pauli_grouping,
            ),
        }
    ]

    warnings: list[str] = []
    x_prev: np.ndarray | None = None
    opt_trace: list[dict[str, Any]] = []

    for level in range(1, vqd.n_states):
        lam = penalties[level - 1]
        x0 = vqd._pick_x0(
            level=level,
            n_param=n_param,
            reused_ground=reused_ground,
            v0_angles=v0_angles,
            x_prev=x_prev,
            rng=rng,
        )

        def objective(
            x: np.ndarray,
            states: list[np.ndarray] = prev_states,
            lam_local: float = lam,
            vqd_level: int = level,
        ) -> float:
            g = vqd._prep(x)
            if vqd.optimizer_mode == "three_computable":
                obj_ch = _vqd_objective_computable(
                    states,
                    g,
                    vqd.hamiltonian.operator,
                    vqd.hamiltonian.n_qubits,
                    shots_objective=shots_objective,
                    rng=rng,
                    pauli_grouping=pauli_grouping,
                )
                ov_ch = _vqd_overlap_computable(
                    states,
                    g,
                    vqd.hamiltonian.operator,
                    vqd.hamiltonian.n_qubits,
                    shots_overlap=shots_overlap,
                    rng=rng,
                )
                wt_ch = _vqd_weight_computable(
                    states,
                    g,
                    vqd.hamiltonian.operator,
                    vqd.hamiltonian.n_qubits,
                    lam_local,
                    shots_overlap=shots_overlap,
                    shots_weight=shots_weight,
                    rng=rng,
                )
                channels = {"objective": obj_ch, "overlap": ov_ch, "weight": wt_ch}
                e = float(channels["objective"].get("energy_exact", 0.0))
                ov = float(channels["overlap"].get("overlap_squared_sum_exact", 0.0))
                wt = float(channels["weight"].get("weight_exact", lam_local * ov))
                opt_trace.append(
                    {
                        "level": vqd_level,
                        "three_protocol": channels,
                        "computable_runtime": [
                            "ExpectationValueComputable",
                            "OverlapSquaredComputable",
                            "vqd_weight_channel",
                        ],
                    }
                )
                return e + wt
            p = float(vqd.overlap_exponent)
            ov_sum = sum(abs(np.vdot(s, g)) ** (2.0 * p) for s in states)
            e = exe.expectation_state(g, vqd.hamiltonian.operator, vqd.hamiltonian.n_qubits)
            return float(e + lam_local * ov_sum)

        r = vqd._minimize(objective, x0)
        x_prev = np.asarray(cast("OptimizeResult", r).x, dtype=float)
        g_new = vqd._prep(x_prev)
        e_new = exe.expectation_state(g_new, vqd.hamiltonian.operator, vqd.hamiltonian.n_qubits)
        energies.append(float(e_new))
        ov_pre = float(sum(abs(np.vdot(s, g_new)) ** 2 for s in prev_states))
        if vqd.max_overlap_warn is not None and ov_pre > float(vqd.max_overlap_warn):
            warnings.append(
                f"level {level}: overlap_squared_sum={ov_pre:.6e} exceeds "
                f"vqd_max_overlap_warn={vqd.max_overlap_warn}"
            )
        tp = _vqd_three_protocol_channels(
            prev_states,
            g_new,
            vqd.hamiltonian.operator,
            vqd.hamiltonian.n_qubits,
            lam,
            shots_objective=shots_objective,
            shots_overlap=shots_overlap,
            shots_weight=shots_weight,
            rng=rng,
            pauli_grouping=pauli_grouping,
        )
        vqd_channels.append(
            {
                "level": level,
                "energy_exact": float(e_new),
                "overlap_squared_sum": ov_pre,
                "orthogonal_weight": lam,
                "channel_note": "objective_plus_overlap_penalty_collapsed_statevector",
                "three_protocol": tp,
            }
        )
        prev_states.append(g_new)

    result_meta = vqd._build_excited_result_meta(
        penalties=penalties,
        vqd_channels=vqd_channels,
        opt_trace=opt_trace,
        warnings=warnings,
        reused_ground=reused_ground,
        shots_objective=shots_objective,
        shots_overlap=shots_overlap,
        shots_weight=shots_weight,
    )
    return VQDResult(energies=energies, meta=result_meta)


__all__ = ["run_vqd_deflation"]

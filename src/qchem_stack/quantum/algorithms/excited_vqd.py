"""Variational quantum deflation (VQD)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast

import numpy as np
from scipy.optimize import minimize

from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.statevector import hea_state

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

from .excited_basis import (
    _vqd_objective_computable,
    _vqd_overlap_computable,
    _vqd_three_protocol_channels,
    _vqd_weight_computable,
    vqd_cross_stack_semantics_meta,
)


@dataclass
class VQDResult:
    energies: list[float]
    meta: dict[str, Any] = field(default_factory=dict)


class VQD:
    """Sequential deflation (Higgott et al., `Quantum 3, 156 (2019)`) with optional three-channel reporting.

    Optimization uses a single classical scalar objective (regularized overlap penalty configurable via
    ``overlap_exponent``). After each level, :func:`_vqd_three_protocol_channels` reports objective /
    overlap / weight statistics analogous to three ``Protocol`` slots (optional shot budgets).

    Optional ``prepare_state`` switches the variational manifold from HEA (:func:`hea_state`) to e.g.
    UCCSD (:meth:`~qchem_stack.quantum.algorithms.uccsd_vqe.UCCSDVQE.prepare_state`).

    **Product / integrator spec (YAML, pipeline wiring, cross-stack meta):** see repository
    ``docs/技术文档_VQD紧缩激发与跨栈对照.md``.
    """

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        n_states: int = 2,
        depth: int = 1,
        penalty_weight: float = 5.0,
        *,
        penalty_weights: list[float] | None = None,
        overlap_exponent: float = 1.0,
        cobyla_maxiter: int = 150,
        optimizer_method: str = "COBYLA",
        prepare_state: Callable[[np.ndarray], np.ndarray] | None = None,
        n_var_parameters: int | None = None,
        parameter_bounds: list[tuple[float, float]] | None = None,
        init_strategy: str = "legacy",
        init_noise_scale: float = 0.15,
        max_overlap_warn: float | None = 0.05,
        overlap_mode: str = "statevector_overlap",
        optimizer_mode: str = "collapsed",
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        self.hamiltonian = hamiltonian
        self.n_states = n_states
        self.depth = depth
        self.penalty_weight = penalty_weight
        self._penalty_weights = list(penalty_weights) if penalty_weights is not None else None
        self.overlap_exponent = float(max(overlap_exponent, 0.05))
        self.cobyla_maxiter = int(max(1, cobyla_maxiter))
        self.optimizer_method = str(optimizer_method).strip().upper()
        self.prepare_state = prepare_state
        self.n_var_parameters = n_var_parameters
        self.parameter_bounds = parameter_bounds
        self.init_strategy = str(init_strategy)
        self.init_noise_scale = float(max(0.0, init_noise_scale))
        self.max_overlap_warn = max_overlap_warn
        self.overlap_mode = str(overlap_mode).strip()
        self.optimizer_mode = str(optimizer_mode).strip().lower()
        if self.overlap_mode not in {
            "statevector_overlap",
            "tangelo_circuit_analogy",
            "deflation_circuit",
        }:
            raise ValueError(
                "VQD overlap_mode must be 'statevector_overlap', "
                "'tangelo_circuit_analogy', or 'deflation_circuit'"
            )
        self._executor = executor

    def _n_params(self) -> int:
        if self.prepare_state is not None:
            if self.n_var_parameters is None:
                raise ValueError("VQD with prepare_state requires n_var_parameters")
            return int(self.n_var_parameters)
        return int(2 * self.hamiltonian.n_qubits * self.depth)

    def _prep(self, x: np.ndarray) -> np.ndarray:
        xv = np.asarray(x, dtype=float).ravel()
        if self.prepare_state is not None:
            g = self.prepare_state(xv)
        else:
            g = hea_state(xv, self.hamiltonian.n_qubits, self.depth)
        g = np.asarray(g, dtype=complex).ravel()
        return cast("np.ndarray", g / (np.linalg.norm(g) + 1e-15))

    def _resolve_penalties(self) -> list[float]:
        n_exc = max(0, self.n_states - 1)
        if n_exc == 0:
            return []
        if self._penalty_weights is not None:
            if len(self._penalty_weights) != n_exc:
                raise ValueError(
                    "penalty_weights must have length n_states - 1 "
                    f"({n_exc}), got {len(self._penalty_weights)}"
                )
            return [float(x) for x in self._penalty_weights]
        return [float(self.penalty_weight)] * n_exc

    def _pick_x0(
        self,
        *,
        level: int,
        n_param: int,
        reused_ground: bool,
        v0_angles: np.ndarray,
        x_prev: np.ndarray | None,
        rng: np.random.Generator,
    ) -> np.ndarray:
        strat = self.init_strategy
        if strat == "legacy":
            if level == 1 and reused_ground and len(v0_angles) == n_param:
                return cast(
                    "np.ndarray",
                    np.asarray(v0_angles, dtype=float).copy(),
                )
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
                + rng.normal(0.0, self.init_noise_scale, size=n_param),
            )
        if (
            strat == "previous_layer_perturb"
            and level > 1
            and x_prev is not None
            and len(x_prev) == n_param
        ):
            return cast(
                "np.ndarray",
                np.asarray(x_prev, dtype=float)
                + rng.normal(0.0, self.init_noise_scale, size=n_param),
            )
        return rng.uniform(-np.pi, np.pi, size=n_param)

    def _minimize(self, objective: Callable[[np.ndarray], float], x0: np.ndarray):
        mi = self.cobyla_maxiter
        m = self.optimizer_method
        if m == "COBYLA":
            return minimize(objective, x0, method="COBYLA", options={"maxiter": mi})
        if m == "NELDER-MEAD":
            return minimize(
                objective,
                x0,
                method="Nelder-Mead",
                options={"maxiter": max(mi, 200)},
            )
        if m == "L-BFGS-B":
            bounds = self.parameter_bounds
            if bounds is None:
                bounds = [(-4.0 * np.pi, 4.0 * np.pi)] * len(x0)
            return minimize(
                objective,
                x0,
                method="L-BFGS-B",
                bounds=bounds,
                options={"maxiter": mi},
            )
        raise ValueError(
            f"Unsupported VQD optimizer_method={self.optimizer_method!r} "
            "(use COBYLA, L-BFGS-B, Nelder-Mead)."
        )

    def _prepare_ground_level(
        self,
        *,
        exe: HamiltonianExpectationExecutor,
        seed: int,
        reused_ground: bool,
        ground_angles: np.ndarray | None,
        ground_energy: float | None,
        n_param: int,
    ) -> tuple[np.ndarray, list[float], np.ndarray]:
        """Prepare level-0 state: reuse the pipeline ground state or run an inner VQE.

        Returns the prepared statevector, the running energy list (seeded with the
        ground energy) and the level-0 angle vector.
        """
        if self.prepare_state is not None and not reused_ground:
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
            g0 = self._prep(ga)
            e0 = (
                float(ground_energy)
                if ground_energy is not None
                else float(
                    exe.expectation_state(g0, self.hamiltonian.operator, self.hamiltonian.n_qubits)
                )
            )
            return g0, [e0], ga
        v0 = VQE(self.hamiltonian, depth=self.depth, executor=exe).run(seed=seed)
        g0 = hea_state(v0.angles, self.hamiltonian.n_qubits, self.depth)
        return g0, [v0.energy], np.asarray(v0.angles, dtype=float)

    def _build_excited_result_meta(
        self,
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
        """Assemble the multi-state VQD result meta (channels, optimizer + semantics)."""
        result_meta: dict[str, Any] = {
            "orthogonal_weight": self.penalty_weight,
            "vqd_penalty_weights_resolved": penalties,
            "reference": "Quantum 3, 156 (2019)",
            "vqd_channels": vqd_channels,
            "implementation_note": "three_protocol_reporting_objective_overlap_weight",
            "shots_objective": shots_objective,
            "shots_overlap": shots_overlap,
            "shots_weight": shots_weight,
            "reused_pipeline_ground": reused_ground,
            "overlap_exponent_yaml": float(self.overlap_exponent),
            "cobyla_maxiter_yaml": int(self.cobyla_maxiter),
            "vqd_optimizer_method": self.optimizer_method,
            "vqd_optimizer_mode": self.optimizer_mode,
            "vqd_optimizer_trace": opt_trace if self.optimizer_mode == "three_computable" else [],
            "vqd_init_strategy_yaml": self.init_strategy,
            "vqd_init_noise_scale_yaml": float(self.init_noise_scale),
            "vqd_overlap_mode_yaml": self.overlap_mode,
            "vqd_variety_yaml": "uccsd" if self.prepare_state else "hea",
        }
        if warnings:
            result_meta["vqd_warnings"] = warnings
        result_meta.update(
            vqd_cross_stack_semantics_meta(
                penalty_weight=self.penalty_weight,
                penalty_weights_resolved=penalties,
                overlap_mode=self.overlap_mode,
                optimizer_mode=self.optimizer_mode,
                n_system_qubits=int(self.hamiltonian.n_qubits),
            )
        )
        return result_meta

    def run(
        self,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
        *,
        shots_objective: int = 0,
        shots_overlap: int = 0,
        shots_weight: int = 0,
        pauli_grouping: str = "tensor_product",
        ground_angles: np.ndarray | None = None,
        ground_energy: float | None = None,
    ) -> VQDResult:
        """Run VQD. If ``ground_angles`` is set (e.g. from pipeline VQE/ADAPT), skip an inner VQE for level 0."""
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        exe = executor or self._executor or StatevectorHeaExecutor()
        rng = np.random.default_rng(seed + 1)
        n_param = self._n_params()
        penalties = self._resolve_penalties()
        reused_ground = ground_angles is not None

        g0, energies, v0_angles = self._prepare_ground_level(
            exe=exe,
            seed=seed,
            reused_ground=reused_ground,
            ground_angles=ground_angles,
            ground_energy=ground_energy,
            n_param=n_param,
        )

        if self.n_states < 2:
            meta = {
                "reference": "Quantum 3, 156 (2019) — collapsed single-objective deflation",
                "reused_pipeline_ground": reused_ground,
                "vqd_variety_yaml": "uccsd" if self.prepare_state else "hea",
            }
            meta.update(
                vqd_cross_stack_semantics_meta(
                    penalty_weight=self.penalty_weight,
                    penalty_weights_resolved=[],
                    overlap_mode=self.overlap_mode,
                )
            )
            return VQDResult(energies=energies, meta=meta)

        lam0 = penalties[0] if penalties else self.penalty_weight
        prev_states: list[np.ndarray] = [g0 / (np.linalg.norm(g0) + 1e-15)]
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
                    self.hamiltonian.operator,
                    self.hamiltonian.n_qubits,
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

        for level in range(1, self.n_states):
            lam = penalties[level - 1]
            x0 = self._pick_x0(
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
                g = self._prep(x)
                if self.optimizer_mode == "three_computable":
                    obj_ch = _vqd_objective_computable(
                        states,
                        g,
                        self.hamiltonian.operator,
                        self.hamiltonian.n_qubits,
                        shots_objective=shots_objective,
                        rng=rng,
                        pauli_grouping=pauli_grouping,
                    )
                    ov_ch = _vqd_overlap_computable(
                        states,
                        g,
                        self.hamiltonian.operator,
                        self.hamiltonian.n_qubits,
                        shots_overlap=shots_overlap,
                        rng=rng,
                    )
                    wt_ch = _vqd_weight_computable(
                        states,
                        g,
                        self.hamiltonian.operator,
                        self.hamiltonian.n_qubits,
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
                p = float(self.overlap_exponent)
                ov_sum = sum(abs(np.vdot(s, g)) ** (2.0 * p) for s in states)
                e = exe.expectation_state(g, self.hamiltonian.operator, self.hamiltonian.n_qubits)
                return float(e + lam_local * ov_sum)

            r = self._minimize(objective, x0)
            x_prev = np.asarray(r.x, dtype=float)
            g_new = self._prep(x_prev)
            e_new = exe.expectation_state(
                g_new, self.hamiltonian.operator, self.hamiltonian.n_qubits
            )
            energies.append(float(e_new))
            ov_pre = float(sum(abs(np.vdot(s, g_new)) ** 2 for s in prev_states))
            if self.max_overlap_warn is not None and ov_pre > float(self.max_overlap_warn):
                warnings.append(
                    f"level {level}: overlap_squared_sum={ov_pre:.6e} exceeds "
                    f"vqd_max_overlap_warn={self.max_overlap_warn}"
                )
            tp = _vqd_three_protocol_channels(
                prev_states,
                g_new,
                self.hamiltonian.operator,
                self.hamiltonian.n_qubits,
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

        result_meta = self._build_excited_result_meta(
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

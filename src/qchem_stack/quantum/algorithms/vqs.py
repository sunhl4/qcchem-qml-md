from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from qchem_stack.quantum.algorithms.base import AlgorithmBase
from qchem_stack.quantum.statevector import hea_state, qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class VQSResult:
    times: list[float]
    trajectory: list[list[float]]
    observables: dict[str, list[float]] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


RhsMode = Literal["linear_damping", "hea_mclachlan_tdvp"]


class AlgorithmVQS(AlgorithmBase):
    """VQS integration for ``O(Delta theta)``: either damped-parameter toy flow or tangent-space TDVP."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        initial_parameters: np.ndarray,
        times: np.ndarray,
        mode: str = "real",
        *,
        rhs_mode: RhsMode = "linear_damping",
        tangent_fd_epsilon: float = 5e-5,
    ) -> None:
        super().__init__()
        self._algorithm_name = "vqs"
        self._report_schema = "algorithm_vqs_report_v1"
        self.hamiltonian = hamiltonian
        self.initial_parameters = np.asarray(initial_parameters, dtype=float)
        self.times = np.asarray(times, dtype=float)
        self.mode = mode
        self.rhs_mode: RhsMode = rhs_mode
        self._tangent_fd_epsilon = float(tangent_fd_epsilon)
        self._last: VQSResult | None = None

    def _hea_depth_from_parameters(self, theta: np.ndarray) -> int:
        nqb = max(1, int(self.hamiltonian.n_qubits))
        denom = 2 * nqb
        if theta.size <= 0 or theta.size % denom != 0:
            raise ValueError(
                f"VQS HEA parameterization expects θ length divisible by {denom}; got {theta.size}."
            )
        return theta.size // denom

    def _linear_damping_rhs(self, theta: np.ndarray) -> np.ndarray:
        sign = 1.0 if self.mode == "real" else -1.0
        return sign * (-0.1 * theta)

    def _hamiltonian_dense(self) -> np.ndarray:
        return qubit_operator_to_sparse(self.hamiltonian.operator, self.hamiltonian.n_qubits)

    def _hea_state_normalized(self, theta: np.ndarray) -> np.ndarray:
        depth = self._hea_depth_from_parameters(theta)
        st = np.asarray(
            hea_state(theta, self.hamiltonian.n_qubits, depth).ravel(), dtype=np.complex128
        )
        nrm = float(np.linalg.norm(st))
        if nrm < 1e-15:
            raise ValueError("HEA state has zero norm in VQS tangent construction.")
        return st / nrm

    def _tan_basis_fd(self, theta: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
        """Normalized reference state ∂|ψ⟩, and centred finite-diff tangent ∂_i ψ."""
        psi0 = self._hea_state_normalized(theta)
        n = theta.size
        eps = float(self._tangent_fd_epsilon)
        basis: list[np.ndarray] = []
        for i in range(n):
            e = np.zeros(n, dtype=float)
            e[i] = eps
            plus = self._hea_state_normalized(theta + e)
            minus = self._hea_state_normalized(theta - e)
            di = (plus - minus) / (2.0 * eps)
            basis.append(np.asarray(di, dtype=np.complex128).ravel())
        return psi0, basis

    def _theta_dot_tdvp(self, theta: np.ndarray) -> np.ndarray:
        h = self._hamiltonian_dense()
        psi0, d_vecs = self._tan_basis_fd(theta)
        hpsi = h @ psi0
        e0 = float(np.real(np.vdot(psi0, hpsi)))
        n = theta.size
        M = np.zeros((n, n), dtype=float)
        rhs = np.zeros(n, dtype=float)
        ridge = 1e-9
        imag_flow = self.mode == "imag"
        for i in range(n):
            for j in range(n):
                gij = np.vdot(d_vecs[i], d_vecs[j])
                if imag_flow:
                    M[i, j] = np.real(gij)
                else:
                    M[i, j] = np.imag(gij)
            if imag_flow:
                rhs[i] = -float(np.real(np.vdot(d_vecs[i], hpsi - e0 * psi0)))
            else:
                rhs[i] = -float(np.real(np.vdot(d_vecs[i], hpsi)))

        Ms = M + ridge * np.eye(n)
        Ms = (Ms + Ms.T) / 2.0
        try:
            sol = np.linalg.solve(Ms, rhs)
        except np.linalg.LinAlgError:
            sol, *_ = np.linalg.lstsq(Ms, rhs, rcond=None)
        sol = np.asarray(sol, dtype=float)
        if not np.all(np.isfinite(sol)):
            sol = np.zeros_like(rhs)
        return sol

    def _theta_dot_step(self, theta: np.ndarray) -> np.ndarray:
        if self.rhs_mode == "linear_damping":
            return self._linear_damping_rhs(theta)
        if self.rhs_mode == "hea_mclachlan_tdvp":
            return self._theta_dot_tdvp(theta)
        raise ValueError(f"Unknown rhs_mode={self.rhs_mode!r}")

    def run(self, **kwargs: Any) -> VQSResult:
        self._ensure_built()
        if self.times.size < 2:
            raise ValueError("times must contain at least two points")
        theta = self.initial_parameters.astype(float).copy()
        traj: list[list[float]] = [theta.tolist()]
        energies: list[float] = []
        h_mat = self._hamiltonian_dense()
        depth = max(1, self._hea_depth_from_parameters(theta))

        tdvp_meta_model = ""
        if self.rhs_mode == "hea_mclachlan_tdvp":
            tdvp_meta_model = "hea_tangent_mcLachlan_fd"

        def energy_at(tvec: np.ndarray) -> float:
            if tvec.size == 2 * self.hamiltonian.n_qubits * depth:
                st = hea_state(tvec, self.hamiltonian.n_qubits, depth)
                return float(np.real(np.vdot(st, h_mat @ st)))
            raise ValueError("internal: HEA θ shape incompatible with tangent depth.")

        rhs_label = self.rhs_mode

        meta_out: dict[str, Any] = {
            "mode": self.mode,
            "n_steps": int(self.times.size - 1),
            "rhs_mode": self.rhs_mode,
            "tangent_finite_difference_epsilon": self._tangent_fd_epsilon,
            "hea_depth": depth,
        }
        if tdvp_meta_model:
            meta_out["rhs_model_tdvp_hint"] = tdvp_meta_model

        for k in range(1, self.times.size):
            dt = float(self.times[k] - self.times[k - 1])
            theta = theta + dt * self._theta_dot_step(theta)
            traj.append(theta.tolist())
            if theta.size == 2 * self.hamiltonian.n_qubits * depth:
                energies.append(float(energy_at(theta)))

        out = VQSResult(
            times=self.times.tolist(),
            trajectory=traj,
            observables={"energy": energies},
            meta=meta_out,
        )
        self._last = out
        self._set_report(
            metrics={"n_steps": out.meta["n_steps"], "hea_depth": depth},
            artifacts={
                "times": out.times,
                "trajectory_len": len(out.trajectory),
                "rhs_model": rhs_label,
            },
            diagnostics={"meta": dict(out.meta)},
        )
        return out


class AlgorithmMcLachlanRealTime(AlgorithmVQS):
    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        initial_parameters: np.ndarray,
        times: np.ndarray,
        *,
        rhs_mode: RhsMode = "linear_damping",
        tangent_fd_epsilon: float = 5e-5,
    ) -> None:
        super().__init__(
            hamiltonian,
            initial_parameters,
            times,
            mode="real",
            rhs_mode=rhs_mode,
            tangent_fd_epsilon=tangent_fd_epsilon,
        )
        self._algorithm_name = "mclachlan_real_time"


class AlgorithmMcLachlanImagTime(AlgorithmVQS):
    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        initial_parameters: np.ndarray,
        times: np.ndarray,
        *,
        rhs_mode: RhsMode = "linear_damping",
        tangent_fd_epsilon: float = 5e-5,
    ) -> None:
        super().__init__(
            hamiltonian,
            initial_parameters,
            times,
            mode="imag",
            rhs_mode=rhs_mode,
            tangent_fd_epsilon=tangent_fd_epsilon,
        )
        self._algorithm_name = "mclachlan_imag_time"

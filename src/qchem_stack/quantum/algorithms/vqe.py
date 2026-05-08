from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from scipy.optimize import minimize

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.base import AlgorithmBase

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


@dataclass
class VQEResult:
    energy: float
    angles: np.ndarray
    nfev: int
    gradient_at_optimum: float | None = None
    auxiliary_values: dict[str, float] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)


class VQE(AlgorithmBase):
    """Variational quantum eigensolver; energy via :class:`HamiltonianExpectationExecutor` (Qiskit / IonStack / NumPy)."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        depth: int = 1,
        executor: HamiltonianExpectationExecutor | None = None,
        objective_expression: Any | None = None,
        auxiliary_expressions: dict[str, Any] | None = None,
        gradient_expression: Any | None = None,
        optimizer_method: str = "COBYLA",
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        super().__init__()
        self._algorithm_name = "vqe"
        self._report_schema = "algorithm_vqe_report_v1"
        self.hamiltonian = hamiltonian
        self.depth = depth
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self.n_params = 2 * self.n_qubits * depth
        self._executor = executor or StatevectorHeaExecutor()
        self._objective_expression = objective_expression
        self._auxiliary_expressions = auxiliary_expressions or {}
        self._gradient_expression = gradient_expression
        self._optimizer_method = optimizer_method
        self._runner: Any | None = None
        self._last_result: VQEResult | None = None

    def build(
        self,
        *,
        protocol_objective: Any | None = None,
        protocol_gradient: Any | None = None,
    ) -> VQE:
        from qchem_stack.protocols.computable import ExpectationValue, ProtocolRunner

        if protocol_objective is not None:
            self._runner = protocol_objective
        else:
            objective = self._objective_expression or ExpectationValue(
                hamiltonian=self.h_op,
                n_qubits=self.n_qubits,
                hea_depth=self.depth,
                executor=self._executor,
            )
            gradient_expr = self._gradient_expression
            if gradient_expr is None and protocol_gradient is not None:
                gradient_expr = protocol_gradient.gradient  # type: ignore[assignment]
            self._runner = ProtocolRunner(
                objective=objective,
                auxiliary=dict(self._auxiliary_expressions),
                gradient=gradient_expr,
            )
        return super().build(
            protocol_objective=protocol_objective is not None,
            protocol_gradient=protocol_gradient is not None,
            optimizer_method=self._optimizer_method,
        )

    def run(
        self,
        maxiter: int = 200,
        initial_parameters: np.ndarray | None = None,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
        *,
        record_energy_trace: bool = False,
    ) -> VQEResult:
        self._ensure_built()
        exe = executor or self._executor
        rng = np.random.default_rng(seed)
        x0 = (
            initial_parameters
            if initial_parameters is not None
            else rng.uniform(-np.pi, np.pi, size=self.n_params)
        )
        nfev = 0
        energy_trace: list[float] = []

        def objective(x: np.ndarray) -> float:
            nonlocal nfev
            nfev += 1
            if self._runner is not None:
                val = float(self._runner.evaluate_objective(np.asarray(x, dtype=float)))
            else:
                val = float(exe.expectation_hea(self.h_op, self.n_qubits, x, self.depth))
            if record_energy_trace:
                energy_trace.append(val)
            return val

        res = minimize(objective, x0, method=self._optimizer_method, options={"maxiter": maxiter})
        aux_vals = (
            self._runner.evaluate_auxiliary(np.asarray(res.x, dtype=float))
            if self._runner is not None
            else {}
        )
        grad_opt = (
            self._runner.evaluate_gradient(np.asarray(res.x, dtype=float))
            if self._runner is not None
            else None
        )
        meta: dict[str, Any] = {
            "scipy_message": str(res.message),
            "optimizer_method": self._optimizer_method,
            "built": True,
        }
        if record_energy_trace:
            meta["energy_trace"] = list(energy_trace)
        out = VQEResult(
            energy=float(res.fun),
            angles=np.asarray(res.x),
            nfev=nfev,
            gradient_at_optimum=grad_opt,
            auxiliary_values=aux_vals,
            meta=meta,
        )
        self._last_result = out
        self._set_report(
            metrics={
                "energy": out.energy,
                "nfev": out.nfev,
                "gradient_at_optimum": out.gradient_at_optimum,
            },
            artifacts={
                "final_parameters": out.angles.tolist(),
                "auxiliary_values": dict(out.auxiliary_values),
            },
            diagnostics={
                "meta": dict(out.meta),
            },
        )
        return out

    def generate_report(self) -> dict[str, Any]:
        if self._last_result is None:
            return super().generate_report()
        r = self._last_result
        return {
            "schema": "algorithm_vqe_report_v1",
            "final_value": float(r.energy),
            "nfev": int(r.nfev),
            "gradient_at_optimum": r.gradient_at_optimum,
            "final_parameters": r.angles.tolist(),
            "auxiliary_values": dict(r.auxiliary_values),
            "meta": dict(r.meta),
        }

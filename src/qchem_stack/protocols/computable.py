"""
Thin computable descriptors for the open stack.

This module attaches **named, serializable** summaries for Methods / parity export
without a second object graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

import numpy as np

from qchem_stack.protocols.computables.refs import ComputableRef, ComputableSpec
from qchem_stack.quantum.algorithms.tolerances import FINITE_DIFFERENCE_STEP
from qchem_stack.quantum.statevector import hea_state, qubit_operator_to_sparse

if TYPE_CHECKING:
    from openfermion.ops.operators.qubit_operator import QubitOperator

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


class Computable(Protocol):
    """Runtime computable primitive consumed by algorithm build/run flows."""

    def evaluate(self, parameters: np.ndarray) -> float | complex: ...


@dataclass
class ExpectationValue:
    """Expectation ``<psi(theta)|H|psi(theta)>`` over an HEA state."""

    hamiltonian: QubitOperator
    n_qubits: int
    hea_depth: int
    executor: HamiltonianExpectationExecutor

    def evaluate(self, parameters: np.ndarray) -> float:
        return float(
            self.executor.expectation_hea(
                self.hamiltonian,
                self.n_qubits,
                np.asarray(parameters, dtype=float),
                self.hea_depth,
            )
        )


@dataclass
class OverlapSquared:
    """Overlap squared between two HEA parameter sets."""

    n_qubits: int
    hea_depth: int
    reference_parameters: np.ndarray

    def evaluate(self, parameters: np.ndarray) -> float:
        psi_ref = hea_state(
            np.asarray(self.reference_parameters, dtype=float), self.n_qubits, self.hea_depth
        )
        psi = hea_state(np.asarray(parameters, dtype=float), self.n_qubits, self.hea_depth)
        return float(abs(np.vdot(psi_ref, psi)) ** 2)


@dataclass
class ExpectationValueDerivative:
    """Finite-difference derivative for an expectation expression."""

    expression: ExpectationValue
    parameter_index: int
    step: float = FINITE_DIFFERENCE_STEP

    def evaluate(self, parameters: np.ndarray) -> float:
        p = np.asarray(parameters, dtype=float).copy()
        i = int(self.parameter_index)
        dp = float(self.step)
        p[i] += dp
        fp = self.expression.evaluate(p)
        p[i] -= 2.0 * dp
        fm = self.expression.evaluate(p)
        return float((fp - fm) / (2.0 * dp))


@dataclass
class MatrixElement:
    """Matrix element ``<left(theta_l)|O|right(theta_r)>`` for HEA states."""

    operator: QubitOperator
    n_qubits: int
    hea_depth: int
    right_parameters: np.ndarray

    def evaluate(self, left_parameters: np.ndarray) -> complex:
        psi_l = hea_state(np.asarray(left_parameters, dtype=float), self.n_qubits, self.hea_depth)
        psi_r = hea_state(
            np.asarray(self.right_parameters, dtype=float), self.n_qubits, self.hea_depth
        )
        op = qubit_operator_to_sparse(self.operator, self.n_qubits)
        return complex(np.vdot(psi_l, op @ psi_r))


@dataclass
class ProtocolRunner:
    """Thin protocol adapter for build/run workflow usage."""

    objective: Computable
    auxiliary: dict[str, Computable] = field(default_factory=dict)
    gradient: Computable | None = None

    def evaluate_objective(self, parameters: np.ndarray) -> float:
        return float(np.real(self.objective.evaluate(parameters)))

    def evaluate_auxiliary(self, parameters: np.ndarray) -> dict[str, float]:
        out: dict[str, float] = {}
        for k, expr in self.auxiliary.items():
            out[k] = float(np.real(expr.evaluate(parameters)))
        return out

    def evaluate_gradient(self, parameters: np.ndarray) -> float | None:
        if self.gradient is None:
            return None
        return float(np.real(self.gradient.evaluate(parameters)))


from qchem_stack.protocols.computables.graph_v2 import (
    refs_from_computable_graph_v2,
    specs_from_computable_graph_v2,
)
from qchem_stack.protocols.computables.list_for_config import (
    assert_computable_workflow_graph_roundtrip,
    computables_export_dict,
    list_computable_specs_for_config,
    list_computables_for_config,
)

__all__ = [
    "Computable",
    "ComputableRef",
    "ComputableSpec",
    "ExpectationValue",
    "ExpectationValueDerivative",
    "MatrixElement",
    "OverlapSquared",
    "ProtocolRunner",
    "assert_computable_workflow_graph_roundtrip",
    "computables_export_dict",
    "list_computable_specs_for_config",
    "list_computables_for_config",
    "refs_from_computable_graph_v2",
    "specs_from_computable_graph_v2",
]

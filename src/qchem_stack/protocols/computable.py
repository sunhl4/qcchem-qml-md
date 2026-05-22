"""
Thin computable descriptors for the open stack.

This module attaches **named, serializable** summaries for Methods / parity export
without a second object graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

import numpy as np

from qchem_stack.config.quantum_helpers import (
    classify_pauli_expectation_path_for_config,
    excited_qse_after_variational,
    excited_sceom_after_variational,
    excited_vqd_after_variational,
    pauli_protocol_enabled,
    qpe_demo_track_requested,
    quantum_workflow_preview_vqs_fields,
    resolve_adapt_max_iter,
    resolve_excited_qse_subspace_dim,
    resolve_excited_sceom_subspace_dim,
    resolve_excited_vqd_n_states,
    resolve_iqeb_max_rounds,
    resolve_pauli_grouping,
    resolve_quantum_algorithm_factory,
    resolve_variational_algorithm,
    resolve_vqe_depth,
    vqs_track_requested,
)
from qchem_stack.quantum.statevector import hea_state, qubit_operator_to_sparse

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.config import ExperimentConfig


@dataclass(frozen=True)
class ComputableRef:
    """A single high-level computational target."""

    name: str
    """E.g. ``ground_state_energy_hea_pauli``."""
    kind: str
    """Coarse class: ``energy``, ``spectrum``, ``phase``."""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComputableSpec:
    """Typed twin of :class:`ComputableRef` for specs / rich workflow export."""

    name: str
    kind: str
    details: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_ref(r: ComputableRef) -> ComputableSpec:
        return ComputableSpec(name=r.name, kind=r.kind, details=dict(r.details))

    def to_ref(self) -> ComputableRef:
        return ComputableRef(name=self.name, kind=self.kind, details=dict(self.details))


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
    step: float = 1e-4

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


def refs_from_computable_graph_v2(graph: dict[str, Any]) -> list[ComputableRef]:
    """Inverse of :func:`~qchem_stack.integrations.workflow_preview.computable_graph_v2` on the ``nodes`` slice.

    Reconstructs refs in **node list order** (same convention as the forward builder). YAML edge
    overrides in the graph are not represented here — re-emit with the same
    :class:`~qchem_stack.config.ExperimentConfig` to restore them.
    """
    from qchem_stack.contracts.schema_ids import COMPUTABLE_GRAPH_V2

    sch = graph.get("schema")
    if sch != COMPUTABLE_GRAPH_V2:
        raise ValueError(f"expected schema {COMPUTABLE_GRAPH_V2!r}, got {sch!r}")
    nodes = graph.get("nodes")
    if not isinstance(nodes, list):
        raise ValueError("computable_graph_v2.nodes must be a list")
    out: list[ComputableRef] = []
    for n in nodes:
        if not isinstance(n, dict):
            raise ValueError("each computable_graph_v2 node must be a dict")
        name, kind = n.get("name"), n.get("kind")
        if name is None or kind is None:
            raise ValueError("each node must have name and kind")
        raw = n.get("details")
        details = dict(raw) if isinstance(raw, dict) else {}
        out.append(ComputableRef(str(name), str(kind), details))
    return out


def specs_from_computable_graph_v2(graph: dict[str, Any]) -> list[ComputableSpec]:
    return [ComputableSpec.from_ref(r) for r in refs_from_computable_graph_v2(graph)]


def list_computables_for_config(cfg: ExperimentConfig) -> list[ComputableRef]:
    """List what the current YAML is configured to *evaluate* (best-effort, documentation-first)."""
    out: list[ComputableRef] = []
    algo = resolve_variational_algorithm(cfg)
    if resolve_quantum_algorithm_factory(cfg):
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {
                    "algorithm_label": algo,
                    "variational_dispatch": "yaml_algorithm_factory_v1",
                    "algorithm_factory": resolve_quantum_algorithm_factory(cfg),
                    "vqe_depth": resolve_vqe_depth(cfg),
                },
            )
        )
    elif algo == "vqe":
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {"algorithm": "vqe", "vqe_depth": resolve_vqe_depth(cfg)},
            )
        )
    elif algo in ("adapt", "tetris_adapt"):
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {"algorithm": algo, "adapt_max_iter": resolve_adapt_max_iter(cfg)},
            )
        )
    elif algo == "iqeb":
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {
                    "algorithm": "iqeb",
                    "iqeb_max_rounds": resolve_iqeb_max_rounds(cfg),
                    "vqe_depth": resolve_vqe_depth(cfg),
                },
            )
        )
    else:
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {
                    "algorithm": algo,
                    "variational_plugin_registry_id": algo,
                    "vqe_depth": resolve_vqe_depth(cfg),
                },
            )
        )
    if pauli_protocol_enabled(cfg):
        out.append(
            ComputableRef(
                "hamiltonian_expectation_pauli_protocol",
                "energy",
                {
                    "pauli_grouping": resolve_pauli_grouping(cfg),
                    "pauli_protocol_expectation_path": classify_pauli_expectation_path_for_config(
                        cfg
                    ),
                },
            )
        )
    if excited_vqd_after_variational(cfg):
        out.append(
            ComputableRef(
                "excited_energies_vqd",
                "spectrum",
                {"n_states": resolve_excited_vqd_n_states(cfg)},
            )
        )
    if excited_qse_after_variational(cfg):
        out.append(
            ComputableRef(
                "excitation_energies_qse",
                "spectrum",
                {"subspace_dim": resolve_excited_qse_subspace_dim(cfg)},
            )
        )
    if excited_sceom_after_variational(cfg):
        out.append(
            ComputableRef(
                "sceom_energies",
                "spectrum",
                {"subspace_dim": resolve_excited_sceom_subspace_dim(cfg)},
            )
        )
    if qpe_demo_track_requested(cfg):
        out.append(
            ComputableRef(
                "qpe_demo_track", "phase", {"hook": "qpe_qec_demo.kitaev + bayesian_stub"}
            )
        )
    if vqs_track_requested(cfg):
        vqs_fields = quantum_workflow_preview_vqs_fields(cfg)
        out.append(
            ComputableRef(
                "vqs_track",
                "dynamics",
                {
                    "hook": "quantum.algorithms.vqs + vqs_pipeline_track",
                    "vqs_mode": vqs_fields["vqs_mode"],
                    "vqs_n_times": vqs_fields["vqs_n_times"],
                },
            )
        )
    return out


def list_computable_specs_for_config(cfg: ExperimentConfig) -> list[ComputableSpec]:
    return [ComputableSpec.from_ref(r) for r in list_computables_for_config(cfg)]


def assert_computable_workflow_graph_roundtrip(cfg: ExperimentConfig) -> None:
    """``computable_graph_v2`` ↔ :func:`refs_from_computable_graph_v2` matches :func:`list_computables_for_config`.

    L1 / wave-F: guarantees workflow-preview DAG nodes round-trip to the same ref list (order + payloads).
    """
    from qchem_stack.integrations.workflow_preview import computable_graph_v2

    refs = list_computables_for_config(cfg)
    graph = computable_graph_v2(refs, cfg)
    back = refs_from_computable_graph_v2(graph)
    assert len(back) == len(refs), (refs, back)
    for a, b in zip(refs, back, strict=True):
        assert a.name == b.name and a.kind == b.kind and a.details == b.details, (a, b)


def computables_export_dict(
    cfg: ExperimentConfig,
    protocol_counts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """JSON-friendly blob for :mod:`scripts.export_parity_criteria_table`.

    When ``protocol_counts`` is passed (e.g. from a finished pipeline run), marks that the
    Pauli support set is available for strict :func:`~qchem_stack.protocols.pauli_support.assert_evaluate_compatible` checks.
    """
    support_from = bool(
        protocol_counts is not None and protocol_counts.get("hamiltonian_pauli_strings") is not None
    )
    return {
        "schema": "qchem_computable_abstract_v2",
        "pauli_protocol_expectation_path": classify_pauli_expectation_path_for_config(cfg),
        "evaluate_note": (
            "Strict evaluate reuse (conservative): each required Pauli label must appear "
            "in hamiltonian_pauli_strings from protocol_counts; see "
            "qchem_stack.protocols.pauli_support.assert_evaluate_compatible."
        ),
        "support_set_exported_from_protocol": support_from,
        "items": [
            {"name": c.name, "kind": c.kind, "details": c.details}
            for c in list_computables_for_config(cfg)
        ],
    }

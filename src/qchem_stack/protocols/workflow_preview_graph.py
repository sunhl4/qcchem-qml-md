"""Computable graph and protocol-stage preview builders."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.config.quantum_helpers import (
    pauli_protocol_enabled,
    resolve_quantum_algorithm_factory,
    resolve_variational_algorithm,
    resolve_variational_ansatz,
)
from qchem_stack.contracts.schema_ids import (
    COMPUTABLE_GRAPH_V1,
    COMPUTABLE_GRAPH_V2,
    VARIATIONAL_YAML_PLUGIN_DISPATCH_V1,
)

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.protocols.computable import ComputableRef

_GROUND = "ground_state_energy"
_PAULI = "hamiltonian_expectation_pauli_protocol"
_EXCITED = frozenset(
    {
        "excited_energies_vqd",
        "excitation_energies_qse",
        "sceom_energies",
        "qpe_demo_track",
        "vqs_track",
    }
)


def protocol_stages_preview_v1(cfg: ExperimentConfig) -> list[dict[str, Any]]:
    return [
        {
            "stage_key": "instantiate",
            "title": "Instantiate",
            "hints": [
                f"molecule_symbols={''.join(cfg.molecule.symbols)}",
                f"basis={cfg.molecule.basis}",
            ],
        },
        {
            "stage_key": "build",
            "title": "Build",
            "hints": [
                f"algorithm={resolve_variational_algorithm(cfg)}",
                f"ansatz={resolve_variational_ansatz(cfg)}",
            ],
        },
        {
            "stage_key": "compile",
            "title": "Compile",
            "hints": [
                f"optimization_level={cfg.compiler.optimization_level}",
                f"native_twoq={cfg.compiler.native_twoq}",
            ],
        },
        {
            "stage_key": "run",
            "title": "Run",
            "hints": [
                f"backend={cfg.backend.name}",
                f"provider={cfg.backend.provider}",
            ],
        },
        {
            "stage_key": "evaluate",
            "title": "Evaluate",
            "hints": [
                "pauli_protocol" if pauli_protocol_enabled(cfg) else "variational_only",
            ],
        },
    ]


def computable_graph_v2(
    refs: list[ComputableRef],
    cfg: ExperimentConfig | None = None,
) -> dict[str, Any]:
    nodes = [
        {"id": f"computable_{i}", "name": r.name, "kind": r.kind, "details": dict(r.details)}
        for i, r in enumerate(refs)
    ]
    name_to_id: dict[str, str] = {}
    for i, r in enumerate(refs):
        name_to_id.setdefault(r.name, f"computable_{i}")

    ground_id = name_to_id.get(_GROUND)
    pauli_id = name_to_id.get(_PAULI)
    anchor = pauli_id or ground_id
    edges: list[dict[str, str]] = []

    for i, r in enumerate(refs):
        nid = f"computable_{i}"
        if r.name == _GROUND:
            continue
        if r.name == _PAULI:
            if ground_id is not None:
                edges.append(
                    {"from": ground_id, "to": nid, "kind": "requires_variational_statevector"}
                )
            continue
        if r.name in _EXCITED:
            if anchor is not None and anchor != nid:
                edges.append({"from": anchor, "to": nid, "kind": "requires_reference_state"})
            continue
        if i > 0:
            edges.append({"from": f"computable_{i - 1}", "to": nid, "kind": "sequential"})

    if cfg is not None:
        q = cfg.quantum
        for rm in q.graph.remove_edges:
            fr = name_to_id.get(rm.from_ref)
            to = name_to_id.get(rm.to_ref)
            if fr is None or to is None:
                continue
            edges = [e for e in edges if not (e["from"] == fr and e["to"] == to)]
        seen = {(e["from"], e["to"]) for e in edges}
        for ex in q.graph.extra_edges:
            fr = name_to_id.get(ex.from_ref)
            to = name_to_id.get(ex.to_ref)
            if fr is None or to is None or fr == to or (fr, to) in seen:
                continue
            edges.append({"from": fr, "to": to, "kind": ex.kind})
            seen.add((fr, to))

    incoming = {e["to"] for e in edges}
    roots = [n["id"] for n in nodes if n["id"] not in incoming]
    out: dict[str, Any] = {
        "schema": COMPUTABLE_GRAPH_V2,
        "edge_model": "semantic_dataflow_v1",
        "nodes": nodes,
        "edges": edges,
        "roots": roots,
    }
    if cfg is not None and (cfg.quantum.graph.extra_edges or cfg.quantum.graph.remove_edges):
        out["declarative_edge_overrides"] = True
    if cfg is not None and resolve_quantum_algorithm_factory(cfg):
        factory = resolve_quantum_algorithm_factory(cfg)
        out["variational_execution"] = {
            "schema": VARIATIONAL_YAML_PLUGIN_DISPATCH_V1,
            "algorithm_factory": factory,
            "algorithm_label": resolve_variational_algorithm(cfg),
            "dag_note": "Variational executor selected via YAML algorithm_factory.",
        }
    return out


def computable_graph_v1(refs: list[ComputableRef]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[list[str]] = []
    prev: str | None = None
    for i, r in enumerate(refs):
        nid = f"computable_{i}"
        nodes.append({"id": nid, "name": r.name, "kind": r.kind, "details": dict(r.details)})
        if prev is not None:
            edges.append([prev, nid])
        prev = nid
    return {"schema": COMPUTABLE_GRAPH_V1, "nodes": nodes, "edges": edges}

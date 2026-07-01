"""Computable graph v2 inverse helpers."""

from __future__ import annotations

from qchem_stack.protocols.computables.refs import ComputableRef, ComputableSpec


def refs_from_computable_graph_v2(graph: dict[str, object]) -> list[ComputableRef]:
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


def specs_from_computable_graph_v2(graph: dict[str, object]) -> list[ComputableSpec]:
    return [ComputableSpec.from_ref(r) for r in refs_from_computable_graph_v2(graph)]

"""P1: mitigation DAG node order matches linear ``qermit_runtime`` trace (L1 audit invariant)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import ExperimentConfig, MitigationSpec, load_experiment_config
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.mitigation.qermit_runtime import execute_mitigation_dag


def _minimal_cfg(**mitigation_patch: object) -> ExperimentConfig:
    p = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(p)
    if not mitigation_patch:
        return cfg
    merged = {**cfg.mitigation.model_dump(mode="python"), **mitigation_patch}
    return cfg.model_copy(update={"mitigation": MitigationSpec.model_validate(merged)})


def _dag_mitigation_kinds(graph: dict) -> list[str]:
    nodes = graph.get("nodes") or []
    kinds = [str(n.get("kind", "")) for n in nodes if str(n.get("id", "")) not in ("in0", "out0")]
    return kinds


def _trace_node_kinds(trace_blob: dict) -> list[str]:
    tr = trace_blob.get("trace") or []
    return [str(step.get("node", "")) for step in tr if isinstance(step, dict)]


@pytest.mark.parametrize(
    "spam,pmsv,zne",
    (
        (False, True, False),
        (False, False, True),
        (True, True, True),
        (True, False, False),
    ),
)
def test_mitigation_graph_topological_order_matches_trace_kinds(
    spam: bool, pmsv: bool, zne: bool
) -> None:
    if not (spam or pmsv or zne):
        pytest.skip("need at least one mitigation stage")
    patch: dict = {}
    if spam:
        patch["stubs"] = {"spam_calibration": True}
    if pmsv:
        patch["pmsv"] = {"enabled": True, "stabilizers": ["Z0"], "retention_rate": 0.9}
    if zne:
        patch["zne"] = {"enabled": True}
    cfg = _minimal_cfg(**patch)
    graph = build_qermit_style_mitigation_report(cfg)
    assert graph is not None
    dag_kinds = _dag_mitigation_kinds(graph)
    dex = execute_mitigation_dag(1.0, 0.01, graph, cfg, protocol_counts={})
    trace_kinds = _trace_node_kinds(dex)
    assert dag_kinds == trace_kinds, (dag_kinds, trace_kinds)
    topo = graph.get("topological_order") or []
    kinds_by_id = {n["id"]: n.get("kind") for n in graph.get("nodes", []) if isinstance(n, dict)}
    topo_kinds_mid = [kinds_by_id[i] for i in topo if i in kinds_by_id and kinds_by_id[i]]
    mid = [k for k in topo_kinds_mid if k not in ("raw_counts_in", "expectation_out")]
    assert mid == trace_kinds


def test_mitigation_graph_schema_propagates_to_runtime_trace() -> None:
    cfg = _minimal_cfg(
        pmsv={"enabled": True, "stabilizers": ["Z0"]},
        zne={"enabled": True},
    )
    graph = build_qermit_style_mitigation_report(cfg)
    assert graph is not None
    dex = execute_mitigation_dag(-0.5, None, graph, cfg, protocol_counts={})
    assert dex.get("graph_schema") == graph.get("schema")


def test_classical_shadows_stub_trace_matches_graph_standalone() -> None:
    cfg = _minimal_cfg(
        stubs={"classical_shadows": True, "classical_shadows_budget_pairs": 64},
    )
    graph = build_qermit_style_mitigation_report(cfg)
    assert graph is not None
    dag_kinds = _dag_mitigation_kinds(graph)
    dex = execute_mitigation_dag(0.12, None, graph, cfg, protocol_counts={})
    trace_kinds = _trace_node_kinds(dex)
    assert dag_kinds == trace_kinds == ["classical_shadows_expectation_stub"]


def test_classical_shadows_stub_between_spam_and_pmsv_matches_trace() -> None:
    cfg = _minimal_cfg(
        stubs={"spam_calibration": True, "classical_shadows": True},
        pmsv={"enabled": True, "stabilizers": ["Z0"], "retention_rate": 0.85},
    )
    graph = build_qermit_style_mitigation_report(cfg)
    assert graph is not None
    dag_kinds = _dag_mitigation_kinds(graph)
    dex = execute_mitigation_dag(-1.1, 0.05, graph, cfg, protocol_counts={})
    trace_kinds = _trace_node_kinds(dex)
    assert dag_kinds == trace_kinds

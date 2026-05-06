"""P1: mitigation DAG node order matches linear ``qermit_runtime`` trace (L1 audit invariant)."""

from __future__ import annotations

import pytest

from qchem_stack.config import ExperimentConfig, MitigationSpec
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.mitigation.qermit_runtime import execute_mitigation_dag


def _minimal_cfg(**mit: object) -> ExperimentConfig:
    from pathlib import Path

    from qchem_stack.config import load_experiment_config

    p = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(p)
    base = MitigationSpec()
    m = base.model_copy(update=dict(mit))
    return cfg.model_copy(update={"mitigation": m})


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
    cfg = _minimal_cfg(
        spam_calibration_enabled=spam,
        pmsv_enabled=pmsv,
        zne_enabled=zne,
        pmsv_stabilizers=["Z0"] if pmsv else [],
        pmsv_retention_rate=0.9 if pmsv else 1.0,
    )
    graph = build_qermit_style_mitigation_report(cfg)
    assert graph is not None
    dag_kinds = _dag_mitigation_kinds(graph)
    dex = execute_mitigation_dag(1.0, 0.01, graph, cfg, protocol_counts={})
    trace_kinds = _trace_node_kinds(dex)
    assert dag_kinds == trace_kinds, (dag_kinds, trace_kinds)
    topo = graph.get("topological_order") or []
    kinds_by_id = {n["id"]: n.get("kind") for n in graph.get("nodes", []) if isinstance(n, dict)}
    topo_kinds_mid = [kinds_by_id[i] for i in topo if i in kinds_by_id and kinds_by_id[i]]
    # Drop raw_counts_in and expectation_out shell kinds for same mid-sequence check
    mid = [k for k in topo_kinds_mid if k not in ("raw_counts_in", "expectation_out")]
    assert mid == trace_kinds


def test_mitigation_graph_schema_propagates_to_runtime_trace() -> None:
    cfg = _minimal_cfg(spam_calibration_enabled=False, pmsv_enabled=True, zne_enabled=True)
    graph = build_qermit_style_mitigation_report(cfg)
    assert graph is not None
    dex = execute_mitigation_dag(-0.5, None, graph, cfg, protocol_counts={})
    assert dex.get("graph_schema") == graph.get("schema")

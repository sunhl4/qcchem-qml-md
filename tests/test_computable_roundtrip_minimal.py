"""B→J 序 21 最小钩：``ComputableRef`` 列表经 ``computable_graph_v2`` 与逆解析一致。"""

from __future__ import annotations

from pathlib import Path

from qchem_stack.config import load_experiment_config
from qchem_stack.integrations.inquanto_workflow_preview import computable_graph_v2
from qchem_stack.protocols.computable import list_computables_for_config, refs_from_computable_graph_v2


def test_computable_refs_roundtrip_via_computable_graph_v2() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    refs = list_computables_for_config(cfg)
    graph = computable_graph_v2(refs, cfg)
    back = refs_from_computable_graph_v2(graph)
    assert [r.name for r in back] == [r.name for r in refs]
    assert [r.kind for r in back] == [r.kind for r in refs]
    assert [r.details for r in back] == [r.details for r in refs]

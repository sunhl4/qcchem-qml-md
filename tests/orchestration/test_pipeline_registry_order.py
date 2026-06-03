"""Pipeline stage registry order matches engineering contract."""

from __future__ import annotations

from qchem_stack.orchestration.stage_registry import PIPELINE_STAGE_SPECS


def test_pipeline_stage_specs_order() -> None:
    names = [spec.name for spec in PIPELINE_STAGE_SPECS]
    assert names == [
        "scf",
        "pre_quantum",
        "variational",
        "embedding_workflow",
        "excited",
        "protocol_finalize",
    ]


def test_pre_quantum_has_post_run_hook() -> None:
    pq = PIPELINE_STAGE_SPECS[1]
    assert pq.name == "pre_quantum"
    assert pq.post_run is not None

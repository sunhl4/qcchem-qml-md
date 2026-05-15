"""P1: ``POST /v1/meta/workflow-preview`` payload matches ``repro.workflow_preview_v1`` (same code path)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.integrations.workflow_preview import (
    slim_product_summary_from_pipeline_result,
    workflow_preview_payload,
)
from qchem_stack.orchestration.pipeline import collect_repro_metadata


def test_workflow_preview_in_collect_matches_standalone() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    repro = collect_repro_metadata(cfg, cfg_path=cfg_path)
    direct = workflow_preview_payload(cfg)
    assert repro["workflow_preview_v1"] == direct


def test_workflow_preview_rich_superset_matches_base_when_stripped() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    base = workflow_preview_payload(cfg, include_computables_rich=False)
    rich = workflow_preview_payload(cfg, include_computables_rich=True)
    cr = rich.get("computables_rich")
    assert cr is not None and cr.get("schema") == "computables_rich_v1"
    lean = {k: v for k, v in rich.items() if k != "computables_rich"}
    assert lean == base


def test_workflow_preview_rich_in_repro_when_parity_flag() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    cfg_on = cfg.model_copy(
        update={
            "parity_integrations": cfg.parity_integrations.model_copy(
                update={"include_computables_rich_in_repro": True}
            )
        }
    )
    repro = collect_repro_metadata(cfg_on, cfg_path=cfg_path)
    assert repro["workflow_preview_v1"] == workflow_preview_payload(
        cfg_on, include_computables_rich=True
    )


def test_slim_summary_surfaces_projection_epistemic_bound() -> None:
    row = {
        "status": "DONE",
        "repro": {
            "experiment_id": "x",
            "embedding_workflow": {
                "mode": "projection",
                "epistemic_bound": "Fragment-local MO screening; not full projection embedding.",
            },
        },
    }
    slim = slim_product_summary_from_pipeline_result(row)
    assert (
        slim.get("embedding_epistemic_bound")
        == row["repro"]["embedding_workflow"]["epistemic_bound"]
    )


@pytest.mark.skipif(
    not Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("configs", "example_h2_vqs_track.yaml")
    .is_file(),
    reason="VQS track sample config missing",
)
def test_workflow_preview_vqs_track_nested_equals_repro_top_level_slice() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2_vqs_track.yaml"
    cfg = load_experiment_config(cfg_path)
    repro = collect_repro_metadata(cfg, cfg_path=cfg_path)
    top = repro.get("workflow_preview_vqs_track_v1")
    assert isinstance(top, dict) and top.get("schema") == "workflow_preview_vqs_track_v1"
    nested = (repro.get("workflow_preview_v1") or {}).get("vqs_track_execution")
    assert nested == top


@pytest.mark.skipif(
    not Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("configs", "qpe_dual_track_demo.yaml")
    .is_file(),
    reason="QPE dual-track sample config missing",
)
def test_workflow_preview_qpe_track_nested_equals_repro_top_level_slice() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "qpe_dual_track_demo.yaml"
    cfg = load_experiment_config(cfg_path)
    repro = collect_repro_metadata(cfg, cfg_path=cfg_path)
    top = repro.get("workflow_preview_qpe_track_v1")
    assert isinstance(top, dict) and top.get("schema") == "workflow_preview_qpe_track_v1"
    nested = (repro.get("workflow_preview_v1") or {}).get("qpe_track_execution")
    assert nested == top

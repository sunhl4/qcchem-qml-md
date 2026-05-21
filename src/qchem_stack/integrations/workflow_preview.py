"""Workflow preview and computable graph exports (facade)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import (
    COMPUTABLES_RICH_V1,
    RUN_PRODUCT_SUMMARY_V1,
    VARIATIONAL_YAML_PLUGIN_DISPATCH_V1,
    WORKFLOW_PREVIEW_QPE_TRACK_V1,
    WORKFLOW_PREVIEW_V1,
    WORKFLOW_PREVIEW_VQS_TRACK_V1,
)
from qchem_stack.integrations.workflow_preview_graph import (
    computable_graph_v1,
    computable_graph_v2,
    protocol_stages_preview_v1,
)
from qchem_stack.protocols.computable import (
    computables_export_dict,
    list_computable_specs_for_config,
    list_computables_for_config,
)

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def workflow_preview_variational_execution_slice_v1(cfg: ExperimentConfig) -> dict[str, Any] | None:
    if not cfg.quantum.algorithm_factory:
        return None
    return {
        "schema": VARIATIONAL_YAML_PLUGIN_DISPATCH_V1,
        "algorithm_factory": cfg.quantum.algorithm_factory,
        "algorithm_label": cfg.quantum.algorithm,
    }


def workflow_preview_vqs_track_slice_v1(cfg: ExperimentConfig) -> dict[str, Any] | None:
    if not cfg.quantum.vqs_track_requested():
        return None
    q = cfg.quantum
    return {
        "schema": WORKFLOW_PREVIEW_VQS_TRACK_V1,
        "vqs_track_after_variational": q.demos.vqs.track_after_variational,
        "vqs_pipeline_integration": q.demos.vqs.pipeline_integration,
        "vqs_mode": q.demos.vqs.mode,
        "vqs_n_times": q.demos.vqs.n_times,
        "vqs_dt": float(q.demos.vqs.dt),
    }


def workflow_preview_qpe_track_slice_v1(cfg: ExperimentConfig) -> dict[str, Any] | None:
    if not cfg.quantum.qpe_demo_track_requested():
        return None
    q = cfg.quantum
    return {
        "schema": WORKFLOW_PREVIEW_QPE_TRACK_V1,
        "qpe_demo_track_after_variational": q.demos.qpe.track_after_variational,
        "qpe_pipeline_integration": q.demos.qpe.pipeline_integration,
        "qpe_demo_track_n_bits": int(q.demos.qpe.demo_track_n_bits),
    }


def workflow_preview_payload(
    cfg: ExperimentConfig,
    *,
    include_computables_rich: bool = False,
) -> dict[str, Any]:
    refs = list_computables_for_config(cfg)
    out: dict[str, Any] = {
        "schema": WORKFLOW_PREVIEW_V1,
        "experiment_id": cfg.experiment_id,
        "protocol_stages": protocol_stages_preview_v1(cfg),
        "computable_graph": computable_graph_v2(refs, cfg),
        "computable_abstract": computables_export_dict(cfg, protocol_counts=None),
    }
    ve = workflow_preview_variational_execution_slice_v1(cfg)
    if ve is not None:
        out["variational_execution"] = ve
    vqs = workflow_preview_vqs_track_slice_v1(cfg)
    if vqs is not None:
        out["vqs_track_execution"] = vqs
    qpe = workflow_preview_qpe_track_slice_v1(cfg)
    if qpe is not None:
        out["qpe_track_execution"] = qpe
    if include_computables_rich:
        specs = list_computable_specs_for_config(cfg)
        out["computables_rich"] = {
            "schema": COMPUTABLES_RICH_V1,
            "n_items": len(specs),
            "items": [{"name": s.name, "kind": s.kind, "details": dict(s.details)} for s in specs],
        }
    return out


def slim_product_summary_from_pipeline_result(row: dict[str, Any]) -> dict[str, Any]:
    status = row.get("status")
    out: dict[str, Any] = {
        "schema": RUN_PRODUCT_SUMMARY_V1,
        "status": status,
        "job_kind": row.get("job_kind"),
    }
    repro_raw = row.get("repro")
    repro: dict[str, Any] = repro_raw if isinstance(repro_raw, dict) else {}
    exp_id = repro.get("experiment_id")
    if exp_id is None and isinstance(row.get("meta"), dict):
        exp_id = row["meta"].get("experiment_id")
    if exp_id is not None:
        out["experiment_id"] = exp_id
    meta = row.get("meta") if isinstance(row.get("meta"), dict) else {}
    if meta:
        api_labels = {
            k: meta[k]
            for k in ("api_workspace_label", "api_project_slug", "nexus_analog_project_label")
            if meta.get(k) is not None and str(meta.get(k)).strip()
        }
        if api_labels:
            out["api_labels"] = api_labels
    if status != "DONE":
        out["partial"] = True
        if row.get("error"):
            out["error_excerpt"] = str(row["error"])[:500]
        return out
    out["partial"] = False
    for key in (
        "scf_energy",
        "energy_after_variational",
        "energy_pauli_protocol",
        "algorithm",
        "nfev",
        "resource_summary",
    ):
        if key in row and row[key] is not None:
            out[key] = row[key]
    ps = repro.get("parity_snapshot")
    if isinstance(ps, dict):
        out["parity_snapshot_keys"] = sorted(ps.keys())
    emb_wf = row.get("embedding_workflow")
    if not isinstance(emb_wf, dict):
        emb_wf = repro.get("embedding_workflow")
    if isinstance(emb_wf, dict):
        bound = emb_wf.get("epistemic_bound")
        if bound is not None:
            out["embedding_epistemic_bound"] = bound
    return out


__all__ = [
    "protocol_stages_preview_v1",
    "computable_graph_v1",
    "computable_graph_v2",
    "workflow_preview_variational_execution_slice_v1",
    "workflow_preview_vqs_track_slice_v1",
    "workflow_preview_qpe_track_slice_v1",
    "workflow_preview_payload",
    "slim_product_summary_from_pipeline_result",
]

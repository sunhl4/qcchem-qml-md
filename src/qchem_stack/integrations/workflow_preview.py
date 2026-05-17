"""Workflow preview and computable graph exports."""

from __future__ import annotations

from typing import Any

from qchem_stack.config import ExperimentConfig
from qchem_stack.protocols.computable import (
    ComputableRef,
    computables_export_dict,
    list_computable_specs_for_config,
    list_computables_for_config,
)

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
                f"algorithm={cfg.quantum.algorithm}",
                f"ansatz={cfg.quantum.variational_ansatz}",
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
                "pauli_protocol" if cfg.quantum.use_pauli_protocol else "variational_only",
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
        for rm in q.computable_remove_edges:
            fr = name_to_id.get(rm.from_ref)
            to = name_to_id.get(rm.to_ref)
            if fr is None or to is None:
                continue
            edges = [e for e in edges if not (e["from"] == fr and e["to"] == to)]
        seen = {(e["from"], e["to"]) for e in edges}
        for ex in q.computable_extra_edges:
            fr = name_to_id.get(ex.from_ref)
            to = name_to_id.get(ex.to_ref)
            if fr is None or to is None or fr == to or (fr, to) in seen:
                continue
            edges.append({"from": fr, "to": to, "kind": ex.kind})
            seen.add((fr, to))

    incoming = {e["to"] for e in edges}
    roots = [n["id"] for n in nodes if n["id"] not in incoming]
    out: dict[str, Any] = {
        "schema": "computable_graph_v2",
        "edge_model": "semantic_dataflow_v1",
        "nodes": nodes,
        "edges": edges,
        "roots": roots,
    }
    if cfg is not None and (cfg.quantum.computable_extra_edges or cfg.quantum.computable_remove_edges):
        out["declarative_edge_overrides"] = True
    if cfg is not None and cfg.quantum.algorithm_factory:
        out["variational_execution"] = {
            "schema": "variational_yaml_plugin_dispatch_v1",
            "algorithm_factory": cfg.quantum.algorithm_factory,
            "algorithm_label": cfg.quantum.algorithm,
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
    return {"schema": "computable_graph_v1", "nodes": nodes, "edges": edges}


def workflow_preview_variational_execution_slice_v1(cfg: ExperimentConfig) -> dict[str, Any] | None:
    if not cfg.quantum.algorithm_factory:
        return None
    return {
        "schema": "variational_yaml_plugin_dispatch_v1",
        "algorithm_factory": cfg.quantum.algorithm_factory,
        "algorithm_label": cfg.quantum.algorithm,
    }


def workflow_preview_vqs_track_slice_v1(cfg: ExperimentConfig) -> dict[str, Any] | None:
    if not cfg.quantum.vqs_track_requested():
        return None
    q = cfg.quantum
    return {
        "schema": "workflow_preview_vqs_track_v1",
        "vqs_track_after_variational": q.vqs_track_after_variational,
        "vqs_pipeline_integration": q.vqs_pipeline_integration,
        "vqs_mode": q.vqs_mode,
        "vqs_n_times": q.vqs_n_times,
        "vqs_dt": float(q.vqs_dt),
    }


def workflow_preview_qpe_track_slice_v1(cfg: ExperimentConfig) -> dict[str, Any] | None:
    if not cfg.quantum.qpe_demo_track_requested():
        return None
    q = cfg.quantum
    return {
        "schema": "workflow_preview_qpe_track_v1",
        "qpe_demo_track_after_variational": q.qpe_demo_track_after_variational,
        "qpe_pipeline_integration": q.qpe_pipeline_integration,
        "qpe_demo_track_n_bits": int(q.qpe_demo_track_n_bits),
    }


def workflow_preview_payload(
    cfg: ExperimentConfig,
    *,
    include_computables_rich: bool = False,
) -> dict[str, Any]:
    refs = list_computables_for_config(cfg)
    out: dict[str, Any] = {
        "schema": "workflow_preview_v1",
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
            "schema": "computables_rich_v1",
            "n_items": len(specs),
            "items": [{"name": s.name, "kind": s.kind, "details": dict(s.details)} for s in specs],
        }
    return out


def slim_product_summary_from_pipeline_result(row: dict[str, Any]) -> dict[str, Any]:
    status = row.get("status")
    out: dict[str, Any] = {
        "schema": "run_product_summary_v1",
        "status": status,
        "job_kind": row.get("job_kind"),
    }
    repro = row.get("repro") if isinstance(row.get("repro"), dict) else {}
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

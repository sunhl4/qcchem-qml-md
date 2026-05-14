"""
InQuanto *public-docs-shaped* workflow preview (open stack).

Maps :class:`~qchem_stack.config.ExperimentConfig` to:
- five narrative protocol stages (instantiate → … → evaluate), aligned with Quantinuum's Protocol overview;
- a small **computable dependency graph** (DAG) so UIs can show an InQuanto-like composable surface without importing closed-source wheels.

This is **L1 contract / UX analogy**, not a claim of binary or API equivalence.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.config import ExperimentConfig
from qchem_stack.protocols.computable import (
    ComputableRef,
    computables_export_dict,
    list_computable_specs_for_config,
    list_computables_for_config,
)


def _hints_instantiate(cfg: ExperimentConfig) -> list[str]:
    mol = cfg.molecule
    sym = "".join(mol.symbols) if mol.symbols else "unknown"
    lines = [
        f"molecule_symbols={sym}",
        f"basis={mol.basis}",
        f"charge={mol.charge} multiplicity={mol.multiplicity}",
    ]
    emb = cfg.embedding
    if emb.dmet_hamiltonian_source:
        lines.append(f"embedding.hamiltonian_source={emb.dmet_hamiltonian_source}")
    return lines


def _hints_build(cfg: ExperimentConfig) -> list[str]:
    q = cfg.quantum
    lines = [f"algorithm={q.algorithm}"]
    if q.algorithm_factory:
        lines.append("variational_dispatch=yaml_algorithm_factory_v1")
        lines.append(f"algorithm_factory={q.algorithm_factory}")
        lines.append(f"VQE-shape depth knob (hea packing) depth={q.vqe_depth}")
    elif q.algorithm == "vqe":
        lines.append(f"VQE depth={q.vqe_depth} maxiter={q.vqe_maxiter}")
        if q.variational_ansatz == "uccsd":
            if q.uccsd_trotter_steps is not None:
                lines.append(
                    f"variational_ansatz=uccsd Trotter layers={int(q.uccsd_trotter_steps)} "
                    "(first-order product formula, JW)"
                )
            else:
                lines.append("variational_ansatz=uccsd (closed-shell cluster exponentials, JW)")
    elif q.algorithm == "adapt":
        lines.append(f"ADAPT max_iter={q.adapt_max_iter}")
    elif q.algorithm == "tetris_adapt":
        lines.append(f"TETRIS_ADAPT max_iter={q.adapt_max_iter}")
    elif q.algorithm == "iqeb":
        lines.append(f"IQEB max_rounds={q.iqeb_max_rounds} inner_VQE_depth={q.vqe_depth}")
    else:
        lines.append(f"registered_variational id={q.algorithm} inner_VQE_depth={q.vqe_depth}")
    lines.append(f"pauli_protocol={'on' if q.use_pauli_protocol else 'off'}")
    return lines


def _hints_compile(cfg: ExperimentConfig) -> list[str]:
    q = cfg.quantum
    c = cfg.compiler
    lines: list[str] = [
        f"optimization_level={c.optimization_level}",
        f"native_twoq={c.native_twoq}",
    ]
    if c.preoptimize_passes:
        lines.append(f"preoptimize_passes={len(c.preoptimize_passes)}")
    if c.compiler_passes:
        lines.append(f"compiler_passes={len(c.compiler_passes)}")
    lines.append(f"pauli_grouping={q.pauli_grouping}")
    integ = cfg.parity_integrations
    if integ.enabled and integ.tket_first_circuit_stats:
        lines.append("tket_first_circuit_stats=True (optional pytket metrics)")
    return lines


def _hints_run(cfg: ExperimentConfig) -> list[str]:
    q = cfg.quantum
    b = cfg.backend
    lines = [f"backend={b.name} provider={b.provider}"]
    if q.run_sampled_pauli_protocol:
        lines.append("Pauli path: statevector grouped shot simulation")
    elif q.run_qiskit_shots_pauli_protocol:
        lines.append("Pauli path: Qiskit shot counts")
    elif q.use_pauli_protocol:
        lines.append("Pauli path: exact/statevector executor")
    if q.vqd_after_variational:
        lines.append(f"VQD n_states={q.vqd_n_states}")
    if q.qse_after_variational:
        lines.append(f"QSE dim={q.qse_subspace_dim}")
    if q.sceom_after_variational:
        lines.append("SCEOM after variational")
    if q.qpe_demo_track_requested():
        lines.append("QPE demo track")
    if q.vqs_track_requested():
        lines.append(f"VQS track mode={q.vqs_mode} n_times={q.vqs_n_times}")
    return lines


def _hints_evaluate(cfg: ExperimentConfig) -> list[str]:
    q = cfg.quantum
    lines: list[str] = []
    if q.use_pauli_protocol:
        lines.append("evaluate: Hamiltonian expectation via Pauli averaging protocol")
    if q.vqd_after_variational or q.qse_after_variational or q.sceom_after_variational:
        lines.append("evaluate: excited-state computables")
    if q.vqs_track_requested():
        lines.append("evaluate: VQS/McLachlan toy trajectory sidecar")
    na = cfg.nexus_analog
    if na.enabled:
        lines.append("sidecar: nexus_analog ledger (local HQC units)")
    m = cfg.mitigation
    if m.zne_enabled or m.pmsv_enabled or m.execution_class != "unspecified":
        lines.append(
            f"mitigation: class={m.execution_class} zne={m.zne_enabled} pmsv={m.pmsv_enabled}"
        )
    if cfg.parity_integrations.enabled and cfg.parity_integrations.open_qermit_reference:
        lines.append("parity: open_qermit_reference (capability matrix in snapshot)")
    return lines or ["evaluate: variational energy only"]


def protocol_stages_preview_v1(cfg: ExperimentConfig) -> list[dict[str, Any]]:
    """Five stages with machine keys + human hints (InQuanto Protocol overview analog)."""
    spec = [
        ("instantiate", "Instantiate", _hints_instantiate),
        ("build", "Build", _hints_build),
        ("compile", "Compile", _hints_compile),
        ("run", "Run", _hints_run),
        ("evaluate", "Evaluate", _hints_evaluate),
    ]
    out: list[dict[str, Any]] = []
    for key, title, fn in spec:
        out.append({"stage_key": key, "title": title, "hints": fn(cfg)})
    return out


_GROUND = "ground_state_energy"
_PAULI = "hamiltonian_expectation_pauli_protocol"
_EXCITED_COMPUTABLES = frozenset(
    {
        "excited_energies_vqd",
        "excitation_energies_qse",
        "sceom_energies",
        "qpe_demo_track",
        "vqs_track",
    }
)


def computable_graph_v2(
    refs: list[ComputableRef],
    cfg: ExperimentConfig | None = None,
) -> dict[str, Any]:
    """
    Semantic dataflow DAG (InQuanto *Computable*-like): Pauli expectation hangs off the variational
    state; excited / phase observables hang off the last variational or Pauli stage.

    Optional YAML: ``quantum.computable_extra_edges`` / ``quantum.computable_remove_edges`` merge on top
    (execution order is **not** changed — graph is for UX / Methods).

    This is an **open approximation** of vendor composable graphs (no fusion / conditional nodes).

    To recover the underlying ref list from JSON, use
    :func:`~qchem_stack.protocols.computable.refs_from_computable_graph_v2` (L1 round-trip with the
    same ``cfg`` for edge overrides).
    """
    nodes: list[dict[str, Any]] = []
    for i, c in enumerate(refs):
        nodes.append(
            {"id": f"computable_{i}", "name": c.name, "kind": c.kind, "details": dict(c.details)}
        )

    name_to_id: dict[str, str] = {}
    for i, c in enumerate(refs):
        if c.name not in name_to_id:
            name_to_id[c.name] = f"computable_{i}"

    ground_id = name_to_id.get(_GROUND)
    pauli_id = name_to_id.get(_PAULI)
    anchor_post_variational = pauli_id if pauli_id is not None else ground_id

    edges: list[dict[str, str]] = []
    for i, c in enumerate(refs):
        nid = f"computable_{i}"
        if c.name == _GROUND:
            continue
        if c.name == _PAULI:
            if ground_id is not None:
                edges.append(
                    {"from": ground_id, "to": nid, "kind": "requires_variational_statevector"}
                )
            continue
        if c.name in _EXCITED_COMPUTABLES:
            if anchor_post_variational is not None and anchor_post_variational != nid:
                edges.append(
                    {"from": anchor_post_variational, "to": nid, "kind": "requires_reference_state"}
                )
            continue
        if i > 0:
            prev = f"computable_{i - 1}"
            if prev != nid:
                edges.append({"from": prev, "to": nid, "kind": "sequential"})

    if cfg is not None:
        q = cfg.quantum
        for rm in q.computable_remove_edges:
            fr = name_to_id.get(rm.from_ref)
            to = name_to_id.get(rm.to_ref)
            if fr is None or to is None:
                continue
            edges = [e for e in edges if not (e["from"] == fr and e["to"] == to)]
        edge_pairs = {(e["from"], e["to"]) for e in edges}
        for ex in q.computable_extra_edges:
            fr = name_to_id.get(ex.from_ref)
            to = name_to_id.get(ex.to_ref)
            if fr is None or to is None or fr == to:
                continue
            if (fr, to) in edge_pairs:
                continue
            edges.append({"from": fr, "to": to, "kind": ex.kind})
            edge_pairs.add((fr, to))

    incoming = {e["to"] for e in edges}
    roots = [n["id"] for n in nodes if n["id"] not in incoming]

    out: dict[str, Any] = {
        "schema": "computable_graph_v2",
        "edge_model": "semantic_dataflow_v1",
        "nodes": nodes,
        "edges": edges,
        "roots": roots,
    }
    if cfg is not None:
        fq = cfg.quantum.algorithm_factory
        if fq:
            out["variational_execution"] = {
                "schema": "variational_yaml_plugin_dispatch_v1",
                "algorithm_factory": fq,
                "algorithm_label": cfg.quantum.algorithm,
                "dag_note": (
                    "ground_state_energy edges match built-in semantics; executor loaded from YAML factory "
                    "at pipeline variational_done."
                ),
            }
    if cfg is not None and (
        cfg.quantum.computable_extra_edges or cfg.quantum.computable_remove_edges
    ):
        out["declarative_edge_overrides"] = True
    return out


def computable_graph_v1(refs: list[ComputableRef]) -> dict[str, Any]:
    """Linear edges in definition order (legacy); prefer :func:`computable_graph_v2` for dashboards."""
    nodes: list[dict[str, Any]] = []
    edges: list[list[str]] = []
    prev: str | None = None
    for i, c in enumerate(refs):
        nid = f"computable_{i}"
        nodes.append({"id": nid, "name": c.name, "kind": c.kind, "details": dict(c.details)})
        if prev is not None:
            edges.append([prev, nid])
        prev = nid
    return {"schema": "computable_graph_v1", "nodes": nodes, "edges": edges}


def workflow_preview_variational_execution_slice_v1(cfg: ExperimentConfig) -> dict[str, Any] | None:
    """Light-weight slice aligned with parity export ``workflow_preview_variational_execution_v1``."""

    fq = cfg.quantum.algorithm_factory
    if not fq:
        return None
    return {
        "schema": "variational_yaml_plugin_dispatch_v1",
        "algorithm_factory": fq,
        "algorithm_label": cfg.quantum.algorithm,
    }


def workflow_preview_vqs_track_slice_v1(cfg: ExperimentConfig) -> dict[str, Any] | None:
    """Config-only slice for VQS/McLachlan sidecar (parity with ``workflow_preview_variational_execution_v1``)."""

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
    """Config-only slice for QPE demo / Kitaev spectral sidecar (parity with ``workflow_preview_vqs_track_v1``)."""

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
    """Single blob for ``POST /v1/meta/workflow-preview``."""
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
    vqs_sl = workflow_preview_vqs_track_slice_v1(cfg)
    if vqs_sl is not None:
        out["vqs_track_execution"] = vqs_sl
    qpe_sl = workflow_preview_qpe_track_slice_v1(cfg)
    if qpe_sl is not None:
        out["qpe_track_execution"] = qpe_sl
    if include_computables_rich:
        specs = list_computable_specs_for_config(cfg)
        out["computables_rich"] = {
            "schema": "computables_rich_v1",
            "n_items": len(specs),
            "items": [{"name": s.name, "kind": s.kind, "details": dict(s.details)} for s in specs],
        }
    return out


def slim_product_summary_from_pipeline_result(row: dict[str, Any]) -> dict[str, Any]:
    """
    Nexust/InQuanto-console-shaped **slim** view from a stored job row or sync result.

    ``row`` is the same shape as :meth:`~qchem_stack.jobs.store.SqliteJobStore.result`.
    """
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
        if meta:
            out["meta"] = meta
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

    sm = repro.get("run_summary") if isinstance(repro.get("run_summary"), dict) else {}
    if sm:
        slim_sm = {k: sm[k] for k in sorted(sm.keys())[:40]}
        out["run_summary"] = slim_sm

    rc = repro.get("run_context") if isinstance(repro.get("run_context"), dict) else {}
    if rc.get("trace_id"):
        out["trace_id"] = rc["trace_id"]

    flags = {
        "nexus_analog_ledger": bool(row.get("nexus_analog_ledger")),
        "mitigation_graph_report": bool(row.get("mitigation_graph_report")),
        "mitigation_dag_execution": bool(row.get("mitigation_dag_execution")),
        "tensornet_protocol_stub": bool(row.get("tensornet_protocol_stub")),
        "qpe_demo_track": bool(row.get("qpe_demo_track")),
        "vqs_track": bool(row.get("vqs_track")),
    }
    out["sidecars_present"] = flags

    ps = repro.get("parity_snapshot")
    if isinstance(ps, dict):
        out["parity_snapshot_keys"] = sorted(ps.keys())

    if isinstance(repro.get("workflow_preview_v1"), dict):
        out["workflow_preview_in_repro"] = True

    ew = repro.get("embedding_workflow")
    if isinstance(ew, dict) and ew.get("epistemic_bound"):
        out["embedding_epistemic_bound"] = str(ew["epistemic_bound"])[:400]

    return out

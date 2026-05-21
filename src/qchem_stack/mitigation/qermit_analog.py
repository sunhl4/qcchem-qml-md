"""
Qermit *style* mitigation **DAG** report (open stack — not Quantinuum Qermit).

Vendor documentation describes :mod:`Qermit` task graphs; we emit nodes + edges + a topological
walk order for auditability (no closed-source Qermit execution).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def build_qermit_style_mitigation_report(cfg: ExperimentConfig) -> dict[str, Any] | None:
    """
    If any mitigation is enabled, return a JSON-serializable task graph
    (input → … → output) for **sequential** SPAM (optional) / classical shadows (optional)
    / PMSV / ZNE composition.
    """
    m = cfg.mitigation
    if not (
        m.pmsv.enabled or m.zne.enabled or m.stubs.spam_calibration or m.stubs.classical_shadows
    ):
        return None

    nodes: list[dict[str, Any]] = [
        {"id": "in0", "kind": "raw_counts_in", "order": 0, "label": "Pauli/shot counts in"},
    ]
    edges: list[dict[str, str]] = []
    order = 0
    prev = "in0"
    if m.stubs.spam_calibration:
        order += 1
        nid = f"n{order}"
        nodes.append(
            {
                "id": nid,
                "kind": "SPAM_readout_calibration_stub",
                "order": order,
                "note": "Affine readout toy (see mitigation.spam); graph order matches runtime trace.",
            }
        )
        edges.append({"source": prev, "target": nid, "dep": "sequential"})
        prev = nid
    if m.stubs.classical_shadows:
        order += 1
        nid = f"n{order}"
        nodes.append(
            {
                "id": nid,
                "kind": "classical_shadows_expectation_stub",
                "order": order,
                "budget_pairs_hint": int(m.stubs.classical_shadows_budget_pairs),
                "note": "Scalar-energy identity stub (no randomized measurement sampling).",
            }
        )
        edges.append({"source": prev, "target": nid, "dep": "sequential"})
        prev = nid
    if m.pmsv.enabled:
        order += 1
        nid = f"n{order}"
        nodes.append(
            {
                "id": nid,
                "kind": "PMSV_symmetry_filter",
                "order": order,
                "stabilizer_count": len(m.pmsv.stabilizers),
                "retention_rate": m.pmsv.retention_rate,
            }
        )
        edges.append({"source": prev, "target": nid, "dep": "sequential"})
        prev = nid
    if m.zne.enabled:
        order += 1
        nid = f"n{order}"
        nodes.append(
            {
                "id": nid,
                "kind": "ZNE_extrapolation_stub",
                "order": order,
                "zne_scales": [float(x) for x in m.zne.scales] if m.zne.scales else [1.0, 1.5, 2.0],
            }
        )
        edges.append({"source": prev, "target": nid, "dep": "sequential"})
        prev = nid
    out_id = "out0"
    order += 1
    nodes.append(
        {
            "id": out_id,
            "kind": "expectation_out",
            "order": order,
            "label": "Energy / observable",
        }
    )
    edges.append({"source": prev, "target": out_id, "dep": "sequential"})

    out = {
        "schema": "qermit_analog_v2",
        "execution_model": "dag",
        "source": "qchem_stack.mitigation.qermit_analog",
        "nodes": nodes,
        "edges": edges,
        "topological_order": [n["id"] for n in nodes],
        "execution_class_manifest": {
            "yaml_execution_class": m.execution_class,
            "async_batch_hint": m.execution_class == "async_batch",
            "sync_graph_hint": m.execution_class == "sync_graph",
            "note": "Manifest encodes intent only; not CQCL MitEx/MitRes binaries.",
        },
    }
    return out

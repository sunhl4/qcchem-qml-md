"""
Field-level **reference** between vendor mitigation narratives (MitRes/Qermit-style) and this repo’s open analogs.

This is documentation-as-data for parity exports — **not** a CQCL binary.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import QERMIT_EXECUTION_OVERLAY_V1, QERMIT_OPEN_REFERENCE_V1

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def qermit_capability_matrix() -> dict[str, Any]:
    """Map named Qermit-style capabilities to ``qchem_stack`` modules and ``MitigationSpec`` knobs."""
    return {
        "schema": QERMIT_OPEN_REFERENCE_V1,
        "disclaimer": "Analog behavior only; not Quantinuum Qermit MitEx/MitRes binaries.",
        "rows": [
            {
                "capability": "Mitigation task graph (DAG)",
                "reference_docs": "Qermit graphs for mitigation stages",
                "implementation": "qchem_stack.mitigation.qermit_analog.build_qermit_style_mitigation_report",
                "export_key": "mitigation_graph_report",
            },
            {
                "capability": "Sequential graph execution",
                "reference_docs": "Runtime consumes graph (MitRes-style)",
                "implementation": "qchem_stack.mitigation.qermit_runtime.execute_mitigation_dag[_runtime]",
                "export_key": "mitigation_dag_execution",
            },
            {
                "capability": "Execution class / batching intent",
                "reference_docs": "Sync vs async barrier semantics on hardware",
                "implementation": "MitigationSpec.execution_class (sync_graph | async_batch | …)",
                "export_key": "repro.parity_snapshot.mitigation_execution_class",
            },
            {
                "capability": "PMSV / symmetry post-selection",
                "reference_docs": "Shot-level filtering",
                "implementation": "Protocol counts + PMSV on PauliAveragingProtocol; toy stderr model in runtime",
                "export_key": "protocol_counts, pmsv_report",
            },
            {
                "capability": "ZNE stub",
                "reference_docs": "Noise scaling / extrapolation",
                "implementation": "qchem_stack.mitigation.zne.zne_scale_energy",
                "export_key": "mitigation_dag_execution trace node ZNE_extrapolation_stub",
            },
        ],
    }


def qermit_mitigation_execution_overlays(cfg: ExperimentConfig) -> dict[str, Any]:
    """Structured **execution-intent** blocks (sync DAG vs async batch) — open stack only."""
    m = cfg.mitigation
    ex = m.execution_class
    out: dict[str, Any] = {
        "schema": QERMIT_EXECUTION_OVERLAY_V1,
        "execution_class": ex,
    }
    if ex == "async_batch":
        out["async_batch_model"] = {
            "fan_out_tasks": ["shot_batches_per_circuit", "mitigation_replicas"],
            "gather": "weighted_expectation_reduction",
            "note": "Python-side serialization only; not CQCL MitEx scheduler.",
        }
    elif ex == "sync_graph":
        out["sync_graph_model"] = {
            "barrier_between_nodes": True,
            "note": "Matches sequential qermit_runtime trace; not hardware barrier timing.",
        }
    elif ex == "shot_postselect":
        out["shot_postselect_model"] = {
            "retention_rate": m.pmsv.retention_rate,
            "kind": "PMSV_style",
        }
    return out

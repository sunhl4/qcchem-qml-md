"""Internal-only compatibility layer for legacy competitor-shaped workflow previews."""

from __future__ import annotations

from qchem_stack.internal_reports.competitor.inquanto_workflow_preview import (
    computable_graph_v2,
    slim_product_summary_from_pipeline_result,
    workflow_preview_payload,
    workflow_preview_qpe_track_slice_v1,
    workflow_preview_variational_execution_slice_v1,
    workflow_preview_vqs_track_slice_v1,
)

__all__ = [
    "computable_graph_v2",
    "slim_product_summary_from_pipeline_result",
    "workflow_preview_payload",
    "workflow_preview_qpe_track_slice_v1",
    "workflow_preview_variational_execution_slice_v1",
    "workflow_preview_vqs_track_slice_v1",
]

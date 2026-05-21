"""Pauli protocol finalize stage (facade; implementation in ``protocol_finalize_*`` modules)."""

from __future__ import annotations

from qchem_stack.orchestration.protocol_finalize_protocol import protocol_for_job
from qchem_stack.orchestration.protocol_finalize_resource import resource_summary_excited_only
from qchem_stack.orchestration.protocol_finalize_run import run_protocol_and_finalize_stage
from qchem_stack.orchestration.protocol_finalize_sidecars import (
    attach_nexus_mitigation_tn,
    attach_qpe_demo_track_if_requested,
    attach_qpe_three_algorithm_pack_if_requested,
    attach_vqs_track_if_requested,
    maybe_attach_md_ml_qmef_dataset,
)

__all__ = [
    "attach_nexus_mitigation_tn",
    "attach_qpe_demo_track_if_requested",
    "attach_qpe_three_algorithm_pack_if_requested",
    "attach_vqs_track_if_requested",
    "maybe_attach_md_ml_qmef_dataset",
    "protocol_for_job",
    "resource_summary_excited_only",
    "run_protocol_and_finalize_stage",
]

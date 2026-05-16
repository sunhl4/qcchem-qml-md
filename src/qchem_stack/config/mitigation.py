"""Mitigation orchestration options for parity and runtime stubs."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class MitigationSpec(BaseModel):
    """Classify mitigation by orchestration topology (sync graph vs async batch)."""

    execution_class: Literal["unspecified", "sync_graph", "async_batch", "shot_postselect"] = (
        "unspecified"
    )
    """``sync_graph``: Qermit-style DAG; ``async_batch``: launch/retrieve-friendly; ``shot_postselect``: PMSV-style."""
    pmsv_enabled: bool = False
    zne_enabled: bool = False
    zne_mode: Literal["scalar_stub", "circuit_scale_fold"] = "scalar_stub"
    """``scalar_stub``: scale energies via :func:`~qchem_stack.mitigation.zne.zne_scale_energy`; ``circuit_scale_fold``: exact HEA-depth amplification per scale (statevector path only; sampled/Qiskit shots fall back to stub)."""
    zne_scales: list[float] = Field(
        default_factory=lambda: [1.0, 1.5, 2.0],
    )
    """Noise-amplified curve abscissas for the open-stack ZNE stub (``zne_scale_energy``) and :mod:`qermit_runtime` execution."""
    pmsv_stabilizers: list[str] = Field(default_factory=list)
    """Symbolic labels (e.g. ``Z0 Z1``) for Methods; toy filter uses :attr:`pmsv_retention_rate` only unless extended."""
    pmsv_retention_rate: float = Field(default=1.0, gt=0.0, le=1.0)
    """Post-selection retention in :math:`(0,1]`; scatters stderr when ``< 1`` (see PMSV stub). Defaults to 1 (no PMSV shot loss)."""
    pmsv_report_extension: str = "default"
    """Hook name for :func:`qchem_stack.mitigation.pmsv.finalize_pmsv_report` (extensible PMSV metadata)."""
    pmsv_extra: dict[str, Any] = Field(default_factory=dict)
    """Opaque key-value pass-through into ``protocol_counts['pmsv_report']`` (plugin / lab metadata)."""
    spam_calibration_enabled: bool = False
    """When true, include a readout-correction stub node in ``mitigation_graph_report`` (before PMSV/ZNE)."""
    pec_literature_stub_enabled: bool = False
    """
    When true, emit ``mitigation_pec_literature_stub_v1`` under ``repro.parity_snapshot`` (P2-W4).

    Literature-facing placeholder for PEC / quasi-probability narratives — **not** Qermit MitRes and not a
    calibrated error cancellation executor.
    """
    classical_shadows_stub_enabled: bool = False
    """
    Insert a ``classical_shadows_expectation_stub`` DAG node + runtime trace (identity on scalar energy).

    Open-stack analog to randomized-measurement narratives in toolboxes such as Tangelo — **no** device
    shadows sampling is performed here.
    """
    classical_shadows_budget_pairs: int = Field(default=256, ge=1, le=10_000_000)
    """Opaque hint integer for Methods export only (not consumed by numeric kernels in this stub)."""

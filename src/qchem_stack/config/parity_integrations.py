"""Optional parity-facing integration sidecars exported into repro payloads."""

from __future__ import annotations

from pydantic import BaseModel


class ParityIntegrationsSpec(BaseModel):
    """
    **Open-stack parity extensions** merged into ``repro.parity_snapshot``.

    Fills reproducibility JSON where vendor defaults are closed: we record *designed* public-contract
    analogs (TKET-shaped compile probe, UCCSD counts, DMET orchestration ledger, qnexus import health,
    Qermit-field mapping, TN strategy map). This is **L1 auditability**, not L0 binary parity with
    closed vendor wheels.
    """

    enabled: bool = True
    qnexus_probe: bool = True
    """``pip install qnexus`` import / version probe (no API calls)."""
    open_qermit_reference: bool = True
    """Static capability matrix vs :mod:`qchem_stack.mitigation.qermit_analog` / ``qermit_runtime``."""
    tensornet_closure_reference: bool = True
    """Strategy map pointing at :mod:`qchem_stack.tensornet.cutensornet_protocol_stub`."""
    uccsd_excitation_reference: bool = True
    """
    Closed-shell **spin-orbital** UCCSD excitation counts from active space
    (:math:`n_{so}=2 n_{active}^{spatial}`, :math:`n_e = n^{active}_{e}`).
    """
    tket_first_circuit_stats: bool = True
    """After Pauli protocol compile, run :func:`~qchem_stack.integrations.tket_fullchain.circuit_ir_to_tket_stats_or_none` on the first compiled ``CircuitIR``."""
    dmet_stub_one_shot_ledger: bool = True
    """When ``embedding.mode`` is ``dmet``, append ``OneShotEmbeddingDriver`` stub run for Methods traceability."""
    gap_closure_reference_bundle: bool = True
    """
    Attach ``open_gap_closure_reference`` (UCC/TKET/Nexus/Qermit/TN/L3/driver matrix) to
    ``parity_snapshot`` — **open engineered references**, not vendor L0 parity.
    """
    include_computables_rich_in_repro: bool = False
    """
    When ``True``, ``repro.workflow_preview_v1`` matches ``POST /v1/meta/workflow-preview`` with
    ``include_computables_rich=True`` (adds ``computables_rich`` / ``computables_rich_v1``).
    Default ``False`` keeps slimmer ``repro``; enable for strict L1 preview↔repro parity tests.
    """

    resource_estimation_preview: bool = False
    """
    When ``True``, ``export_parity_criteria_table`` may emit ``resource_estimation_preview_v1``
    (P2-W1 shallow Methods/resource narrative; no cloud pricing).
    """

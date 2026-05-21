"""Optional parity-facing integration sidecars exported into repro payloads."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ParityIntegrationsSpec(BaseModel):
    """
    **Open-stack parity extensions** merged into ``repro.parity_snapshot``.

    Fills reproducibility JSON where vendor defaults are closed: we record *designed* public-contract
    analogs (TKET-shaped compile probe, UCCSD counts, DMET orchestration ledger, qnexus import health,
    Qermit-field mapping, TN strategy map). This is **L1 auditability**, not L0 binary parity with
    closed vendor wheels.
    """

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(
        default=True, description="Master switch for parity sidecars in repro export."
    )
    qnexus_probe: bool = Field(
        default=True,
        description="``pip install qnexus`` import / version probe (no API calls).",
    )
    open_qermit_reference: bool = Field(
        default=True,
        description="Static capability matrix vs :mod:`qchem_stack.mitigation.qermit_analog` / ``qermit_runtime``.",
    )
    tensornet_closure_reference: bool = Field(
        default=True,
        description="Strategy map pointing at :mod:`qchem_stack.tensornet.cutensornet_protocol_stub`.",
    )
    uccsd_excitation_reference: bool = Field(
        default=True,
        description=(
            "Closed-shell spin-orbital UCCSD excitation counts from active space "
            "(n_so=2*n_active_spatial, n_e=n_active_electrons)."
        ),
    )
    tket_first_circuit_stats: bool = Field(
        default=True,
        description=(
            "After Pauli protocol compile, run "
            ":func:`~qchem_stack.integrations.tket_fullchain.circuit_ir_to_tket_stats_or_none` "
            "on the first compiled ``CircuitIR``."
        ),
    )
    dmet_stub_one_shot_ledger: bool = Field(
        default=True,
        description="When ``embedding.mode`` is ``dmet``, append ``OneShotEmbeddingDriver`` stub run for Methods traceability.",
    )
    gap_closure_reference_bundle: bool = Field(
        default=True,
        description=(
            "Attach ``open_gap_closure_reference`` (UCC/TKET/Nexus/Qermit/TN/L3/driver matrix) to "
            "``parity_snapshot`` — open engineered references, not vendor L0 parity."
        ),
    )
    include_computables_rich_in_repro: bool = Field(
        default=False,
        description=(
            "When True, ``repro.workflow_preview_v1`` matches ``POST /v1/meta/workflow-preview`` with "
            "``include_computables_rich=True``. Default False keeps slimmer repro."
        ),
    )
    resource_estimation_preview: bool = Field(
        default=False,
        description=(
            "When True, ``export_parity_criteria_table`` may emit ``resource_estimation_preview_v1`` "
            "(P2-W1 shallow Methods/resource narrative; no cloud pricing)."
        ),
    )

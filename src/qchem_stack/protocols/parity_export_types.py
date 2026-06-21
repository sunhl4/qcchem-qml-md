"""TypedDict contracts for parity export v3 JSON documents."""

from __future__ import annotations

from typing import Any, TypedDict, cast

from qchem_stack.protocols.product_contract_export import PARITY_EXPORT_V3_STABLE_KEYS


class ComputableAbstractV2(TypedDict, total=False):
    """Top-level ``computable_abstract`` block (``qchem_computable_abstract_v2``)."""

    schema: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


class ParityExportV3Document(TypedDict, total=False):
    """Config-only or run-merged parity export (schema version 3)."""

    parity_export_schema_version: str
    experiment_id: str
    computable_abstract: ComputableAbstractV2 | dict[str, Any]
    excited_resource_from_config: dict[str, Any]
    capability_gap_categories: list[dict[str, Any]]
    iqeb_implementation_path: str
    pauli_protocol_expectation_path: str
    protocol_expectation_semantics_v1: dict[str, Any]
    geometry_source: dict[str, Any]
    embedding: dict[str, Any]
    pre_quantum_semantics_from_config: dict[str, Any]
    resource_estimation_preview_v1: dict[str, Any]
    methods_resource_unified_v1: dict[str, Any]
    scf_energy_from_run: float
    energy_after_variational_from_run: float
    energy_pauli_protocol_from_run: float
    parity_snapshot_from_run: dict[str, Any]
    run_summary_from_repro: dict[str, Any]


def assert_stable_keys_present(doc: ParityExportV3Document | dict[str, Any]) -> None:
    """Config-only export must expose registered stable top-level keys."""
    table = cast("dict[str, Any]", doc)
    if table.get("parity_export_schema_version") != "3":
        raise ValueError("parity_export_schema_version must be '3'")
    missing = sorted(PARITY_EXPORT_V3_STABLE_KEYS - set(table.keys()))
    if missing:
        raise ValueError(f"parity export missing stable keys: {missing}")


def as_parity_export_v3(doc: dict[str, Any]) -> ParityExportV3Document:
    """Narrow a built export dict to the v3 document type."""
    return cast("ParityExportV3Document", doc)


__all__ = [
    "ComputableAbstractV2",
    "ParityExportV3Document",
    "assert_stable_keys_present",
    "as_parity_export_v3",
]

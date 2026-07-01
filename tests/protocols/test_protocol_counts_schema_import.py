"""Import smoke for TypedDict-only protocol count export shapes."""

from __future__ import annotations


def test_protocol_counts_schema_symbols_importable() -> None:
    from qchem_stack.protocols import protocol_counts_schema as mod

    assert mod.ProtocolCountsExportV1 is not None
    assert mod.ResourceRowExportV1 is not None

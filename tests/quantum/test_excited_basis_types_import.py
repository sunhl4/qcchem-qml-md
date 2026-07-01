"""Import smoke for TypedDict-only excited basis export shapes."""

from __future__ import annotations


def test_excited_basis_types_symbols_importable() -> None:
    from qchem_stack.quantum.algorithms import excited_basis_types as mod

    assert mod.VqdObjectiveChannelV1 is not None
    assert mod.VqdCrossStackSemanticsV1 is not None
    assert mod.VqdDeflationCircuitSketchV1 is not None

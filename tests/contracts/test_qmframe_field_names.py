"""QMFrame export field names stay aligned with md_bridge schema."""

from __future__ import annotations

from qchem_stack.contracts.qmframe_field_names import qmframe_field_names_v1
from qchem_stack.md_bridge.schema import QMFrame


def test_qmframe_field_names_match_schema() -> None:
    assert qmframe_field_names_v1() == sorted(QMFrame.model_fields.keys())

"""D22: every `MitigationSpec` field name appears in mitigation mapping doc (YAML audit trail)."""

from __future__ import annotations

from pathlib import Path

from qchem_stack.config import MitigationSpec

_DOC = Path(__file__).resolve().parents[1] / "docs" / "mitigation_PMSV_ZNE_Qermit_mapping.md"


def test_mitigation_mapping_doc_indexes_all_spec_fields() -> None:
    text = _DOC.read_text(encoding="utf-8")
    marker = "### MitigationSpec YAML 键（机读审计）"
    assert marker in text
    idx = text.index(marker)
    tail = text[idx : idx + 800]
    for name in MitigationSpec.model_fields:
        assert name in tail, f"{name} missing near mitigation audit subsection"

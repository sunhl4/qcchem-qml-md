"""D22: every `MitigationSpec` field name appears in mitigation mapping doc (YAML audit trail)."""

from __future__ import annotations

from qchem_stack.config import MitigationSpec
from tests.helpers.paths import docs_path

_DOC = docs_path("mitigation_PMSV_ZNE_Qermit_mapping.md")


def _mitigation_yaml_paths() -> list[str]:
    paths: list[str] = []
    for name, field in MitigationSpec.model_fields.items():
        ann = field.annotation
        if isinstance(ann, type) and hasattr(ann, "model_fields"):
            for sub in ann.model_fields:
                paths.append(f"{name}.{sub}")
        else:
            paths.append(name)
    return paths


def test_mitigation_mapping_doc_indexes_all_spec_fields() -> None:
    text = _DOC.read_text(encoding="utf-8")
    marker = "### MitigationSpec YAML 键（机读审计）"
    assert marker in text
    idx = text.index(marker)
    tail = text[idx : idx + 1200]
    for name in _mitigation_yaml_paths():
        assert name in tail, f"{name} missing near mitigation audit subsection"

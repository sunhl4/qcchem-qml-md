"""P2-W4：缓解映射文档含双月进阶占位节（防漂移）。"""

from __future__ import annotations

from tests.helpers.paths import docs_path


def test_mitigation_mapping_has_p2_advanced_block() -> None:
    p = docs_path("mitigation_PMSV_ZNE_Qermit_mapping.md")
    text = p.read_text(encoding="utf-8")
    assert "P2 进阶块" in text
    assert "PEC" in text

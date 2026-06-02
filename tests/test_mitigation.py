"""Mitigation subsystem tests: PMSV, async queue, documentation audit.

Consolidates:
- test_mitigation_p2_doc_anchor.py
- test_mitigation_async_queue.py
- test_pmsv_finalize.py
- test_mitigation_spec_doc_audit.py
"""

from __future__ import annotations

import asyncio

from qchem_stack.config import MitigationSpec
from qchem_stack.jobs.mitigation_queue import LocalMitigationJobQueue
from qchem_stack.mitigation.pmsv import PMSVConfig, finalize_pmsv_report
from tests.helpers.paths import docs_path


class TestPMSVReport:
    """PMSV report extension and extra merge."""

    def test_finalize_pmsv_report_merges_extra(self) -> None:
        p = PMSVConfig(
            stabilizers=["Z0"],
            retention_rate=0.9,
            report_extension="lab_a",
            extra={"note": "methods"},
        )
        out = finalize_pmsv_report(
            {"stabilizers": ["Z0"], "retention_rate": 0.9},
            p,
        )
        assert out["report_extension"] == "lab_a"
        assert out["extra"]["note"] == "methods"


class TestMitigationAsyncQueue:
    """Local mitigation async queue."""

    def test_drain_all_processes_all_jobs(self) -> None:
        q = LocalMitigationJobQueue()
        for i in range(3):
            q.submit(f"j{i}", {"i": i})

        async def _run() -> list:
            return await q.drain_all(lambda p: {"echo": p["i"]}, concurrency=2)

        done = asyncio.run(_run())
        assert len(done) == 3
        assert q.stats()["pending"] == 0
        assert q.stats()["completed"] == 3


class TestMitigationDocumentationAudit:
    """D22: MitigationSpec field documentation audit.

    Every MitigationSpec field name appears in mitigation mapping doc
    (YAML audit trail).
    """

    def _mitigation_yaml_paths(self) -> list[str]:
        paths: list[str] = []
        for name, field in MitigationSpec.model_fields.items():
            ann = field.annotation
            if isinstance(ann, type) and hasattr(ann, "model_fields"):
                for sub in ann.model_fields:
                    paths.append(f"{name}.{sub}")
            else:
                paths.append(name)
        return paths

    def test_mitigation_mapping_doc_indexes_all_spec_fields(self) -> None:
        doc = docs_path("mitigation_PMSV_ZNE_Qermit_mapping.md")
        text = doc.read_text(encoding="utf-8")
        marker = "### MitigationSpec YAML 键（机读审计）"
        assert marker in text
        idx = text.index(marker)
        tail = text[idx : idx + 1200]
        for name in self._mitigation_yaml_paths():
            assert name in tail, f"{name} missing near mitigation audit subsection"

    def test_mitigation_mapping_has_p2_advanced_block(self) -> None:
        """P2-W4: mitigation mapping doc has P2 advanced placeholder section."""
        doc = docs_path("mitigation_PMSV_ZNE_Qermit_mapping.md")
        text = doc.read_text(encoding="utf-8")
        assert "P2 进阶块" in text
        assert "PEC" in text

"""PMSV report extension / extra merge."""

from __future__ import annotations

from qchem_stack.mitigation.pmsv import PMSVConfig, finalize_pmsv_report


def test_finalize_pmsv_report_merges_extra() -> None:
    p = PMSVConfig(
        stabilizers=["Z0"],
        retention_rate=0.9,
        report_extension="lab_a",
        extra={"note": "methods"},
    )
    out = finalize_pmsv_report({"stabilizers": ["Z0"], "retention_rate": 0.9}, p)
    assert out["report_extension"] == "lab_a"
    assert out["extra"]["note"] == "methods"

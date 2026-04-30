"""L3 benchmark suite: schema / env-gated heavy runs (see docs/L3_benchmark_suite_roadmap.md)."""

from __future__ import annotations

import os

import pytest

pytestmark = [pytest.mark.l3]


def test_l3_benchmark_placeholder_skipped_by_default() -> None:
    """Full L3 asserts run only when QCHEM_RUN_L3=1 (optional CI job)."""
    if os.environ.get("QCHEM_RUN_L3", "").strip() != "1":
        pytest.skip("Set QCHEM_RUN_L3=1 to run L3 numerical benchmarks (see docs/L3_benchmark_suite_roadmap.md)")

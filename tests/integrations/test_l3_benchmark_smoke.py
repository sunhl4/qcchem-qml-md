"""L3 benchmark suite: optional representative algorithm pipelines (appendix B §7 style)."""

from __future__ import annotations

import math
import os

import pytest

from qchem_stack.integrations.l3_algorithm_benchmark import (
    L3_PYTEST_YAMLS,
    algorithm_benchmark_bundle_v1,
    merged_experiment_benchmark_v1,
)
from tests.helpers.paths import repo_root

pytestmark = [pytest.mark.l3]


def test_l3_representative_algorithm_yamls_sync_pipeline() -> None:
    """Energy + run_summary smoke; when enabled, emits ``algorithm_benchmark_bundle_v1`` metrics."""
    if os.environ.get("QCHEM_RUN_L3", "").strip() != "1":
        pytest.skip(
            "Set QCHEM_RUN_L3=1 to run L3 numerical benchmarks (see docs/public_parity_matrix.md 附录 B §7)"
        )
    pytest.importorskip("pyscf")
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    root = repo_root()
    for rel in L3_PYTEST_YAMLS:
        assert (root / rel).is_file(), f"missing L3 representative config: {rel}"

    bundle = algorithm_benchmark_bundle_v1(
        repo_root=root,
        config_rels=list(L3_PYTEST_YAMLS),
        run_sync=run_pipeline_sync,
    )
    assert bundle["schema"] == "algorithm_benchmark_bundle_v1"
    assert len(bundle["rows"]) == len(L3_PYTEST_YAMLS)
    for row in bundle["rows"]:
        assert row["wall_time_ms"] >= 0.0
        energy = float(row["energy_after_variational_au"])
        assert math.isfinite(energy)
        assert isinstance(row.get("stages_completed_tail"), list)
    merged = merged_experiment_benchmark_v1(bundle)
    assert merged["schema"] == "merged_experiment_benchmark_v1"
    assert merged["n_configs"] == len(bundle["rows"])
    assert merged["total_wall_time_ms"] is not None and merged["total_wall_time_ms"] > 0
    by_algo = merged.get("by_quantum_algorithm_yaml")
    assert isinstance(by_algo, list) and len(by_algo) >= 1
    assert sum(g["n_configs"] for g in by_algo) == merged["n_configs"]

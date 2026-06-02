from __future__ import annotations

from pathlib import Path

from qchem_stack.quantum.l3_algorithm_benchmark import (
    DEFAULT_BENCHMARK_YAMLS,
    algorithm_benchmark_bundle_v1,
    merged_experiment_benchmark_v1,
)


def test_algorithm_benchmark_bundle_missing_files_yields_empty_rows() -> None:
    b = algorithm_benchmark_bundle_v1(
        repo_root=Path("/nonexistent_root"), config_rels=["nope.yaml"]
    )
    assert b["schema"] == "algorithm_benchmark_bundle_v1"
    assert b["rows"] == []


def test_merged_experiment_benchmark_empty() -> None:
    m = merged_experiment_benchmark_v1({"schema": "algorithm_benchmark_bundle_v1", "rows": []})
    assert m["schema"] == "merged_experiment_benchmark_v1"
    assert m["n_configs"] == 0
    assert m["total_wall_time_ms"] is None
    assert m["by_quantum_algorithm_yaml"] == []


def test_merged_experiment_benchmark_groups_by_algorithm_yaml() -> None:
    bundle = {
        "schema": "algorithm_benchmark_bundle_v1",
        "rows": [
            {"quantum_algorithm_yaml": "adapt_v1", "wall_time_ms": 10.0},
            {"quantum_algorithm_yaml": "adapt_v1", "wall_time_ms": 20.0},
            {"quantum_algorithm_yaml": "iqeb_v1", "wall_time_ms": 5.0},
            {"quantum_algorithm_yaml": None, "wall_time_ms": 1.0},
        ],
    }
    m = merged_experiment_benchmark_v1(bundle)
    assert m["n_configs"] == 4
    assert m["total_wall_time_ms"] == 36.0
    assert m["mean_wall_time_ms"] == 9.0
    keys = [
        (g["quantum_algorithm_yaml"], g["n_configs"], g["total_wall_time_ms"])
        for g in m["by_quantum_algorithm_yaml"]
    ]
    assert keys == [
        (None, 1, 1.0),
        ("adapt_v1", 2, 30.0),
        ("iqeb_v1", 1, 5.0),
    ]


def test_default_benchmark_yaml_set_covers_reference_and_tangelo_slices() -> None:
    # Reference-demo aligned: VQD UCCSD deflation sample.
    assert "configs/example_h2_vqd_uccsd.yaml" in DEFAULT_BENCHMARK_YAMLS
    # Tangelo-aligned: fermion mapping / pool-alias vocabulary sample.
    assert "configs/example_h2_iqeb_qubit_excitation_alias.yaml" in DEFAULT_BENCHMARK_YAMLS

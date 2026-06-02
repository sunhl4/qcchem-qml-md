from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from tests.helpers.paths import repo_root


def _load_generate_module():
    script = repo_root() / "scripts" / "benchmark_dashboard" / "generate.py"
    spec = importlib.util.spec_from_file_location("_bench_dash", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_render_html_includes_rows_and_merged_summary() -> None:
    mod = _load_generate_module()
    report = {
        "algorithm_benchmark_bundle_v1": {
            "schema": "algorithm_benchmark_bundle_v1",
            "rows": [
                {
                    "experiment_id": "h2_demo",
                    "config_rel": "configs/example_h2.yaml",
                    "quantum_algorithm_yaml": "vqe",
                    "scf_energy_au": -1.12,
                    "energy_after_variational_au": -1.13,
                    "nfev": 12,
                    "wall_time_ms": 42.5,
                }
            ],
        },
        "merged_experiment_benchmark_v1": {
            "schema": "merged_experiment_benchmark_v1",
            "n_configs": 1,
            "total_wall_time_ms": 42.5,
            "mean_wall_time_ms": 42.5,
            "by_quantum_algorithm_yaml": [
                {
                    "quantum_algorithm_yaml": "vqe",
                    "n_configs": 1,
                    "total_wall_time_ms": 42.5,
                    "mean_wall_time_ms": 42.5,
                }
            ],
        },
    }
    html_doc = mod.render_html(report)
    assert "algorithm_benchmark_bundle_v1" in html_doc
    assert "configs/example_h2.yaml" in html_doc
    assert "h2_demo" in html_doc
    assert "By quantum algorithm" in html_doc
    assert "42.5" in html_doc


def test_render_html_includes_pipeline_profile_section() -> None:
    mod = _load_generate_module()
    profile = {
        "schema": "pipeline_profile_v1",
        "stages": [{"stage": "scf_done", "duration_ms": 12.3, "peak_memory_kb": 1024}],
    }
    html_doc = mod.render_html({}, pipeline_profile=profile)
    assert "Pipeline profile" in html_doc
    assert "scf_done" in html_doc


def test_load_report_json_from_stdin(tmp_path: Path) -> None:
    mod = _load_generate_module()
    payload = {
        "algorithm_benchmark_bundle_v1": {"schema": "algorithm_benchmark_bundle_v1", "rows": []}
    }
    inp = tmp_path / "l3.json"
    inp.write_text(json.dumps(payload), encoding="utf-8")
    loaded = mod.load_report_json(input_path=inp)
    assert loaded["algorithm_benchmark_bundle_v1"]["rows"] == []


def test_main_writes_output_file(tmp_path: Path) -> None:
    mod = _load_generate_module()
    payload = {
        "algorithm_benchmark_bundle_v1": {
            "schema": "algorithm_benchmark_bundle_v1",
            "rows": [{"experiment_id": "x", "config_rel": "c.yaml", "wall_time_ms": 1.0}],
        }
    }
    inp = tmp_path / "in.json"
    out = tmp_path / "out.html"
    inp.write_text(json.dumps(payload), encoding="utf-8")

    argv = ["generate.py", "--input", str(inp), "--output", str(out)]
    old_argv = sys.argv
    try:
        sys.argv = argv
        mod.main()
    finally:
        sys.argv = old_argv

    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in text
    assert "c.yaml" in text

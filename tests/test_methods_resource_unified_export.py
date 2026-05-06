"""Wave D: ``methods_resource_unified_v1`` / preview in parity export."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]


def test_methods_resource_preview_in_config_only_export() -> None:
    import importlib.util

    ep_path = _ROOT / "scripts" / "export_parity_criteria_table.py"
    spec = importlib.util.spec_from_file_location("export_parity_criteria_table", ep_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    d = mod._table_from_config(_ROOT / "configs" / "qpe_dual_track_demo.yaml")
    prev = d.get("methods_resource_preview_v1")
    assert isinstance(prev, dict)
    assert prev.get("schema") == "methods_resource_preview_v1"
    assert prev.get("qpe_pipeline_integration") is True


def _export_with_results(cfg_rel: str, results: Path) -> dict:
    env = {**os.environ, "PYTHONPATH": str(_ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", "")}
    cmd = [
        sys.executable,
        str(_ROOT / "scripts" / "export_parity_criteria_table.py"),
        str(_ROOT / cfg_rel),
        "--results",
        str(results),
    ]
    proc = subprocess.run(cmd, cwd=str(_ROOT), capture_output=True, text=True, env=env, check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return json.loads(proc.stdout)


@pytest.mark.skipif(
    not (_ROOT / "configs" / "qpe_dual_track_demo.yaml").is_file(),
    reason="config missing",
)
def test_methods_resource_unified_from_qpe_dual_track_pipeline() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")

    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = _ROOT / "configs" / "qpe_dual_track_demo.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    tmp = _ROOT / "tests" / "fixtures" / "_tmp_qpe_dual_methods_resource.json"
    try:
        tmp.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        exp = _export_with_results("configs/qpe_dual_track_demo.yaml", tmp)
    finally:
        tmp.unlink(missing_ok=True)

    uni = exp.get("methods_resource_unified_v1")
    assert isinstance(uni, dict)
    assert uni.get("schema") == "methods_resource_unified_v1"
    assert isinstance(uni.get("resource_summary"), dict)
    assert uni.get("run_summary_qpe_demo_track_ran") is True
    qpeb = uni.get("qpe_demo_track")
    assert isinstance(qpeb, dict)
    assert qpeb.get("schema")


@pytest.mark.skipif(
    not (_ROOT / "configs" / "example_h2_qpe_track_parity_integrations.yaml").is_file(),
    reason="config missing",
)
def test_methods_resource_unified_qpe_plus_tket_probe_schema() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("pytket")

    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_rel = "configs/example_h2_qpe_track_parity_integrations.yaml"
    cfg_path = _ROOT / cfg_rel
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    tmp = _ROOT / "tests" / "fixtures" / "_tmp_methods_resource_qpe_tket.json"
    try:
        tmp.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        exp = _export_with_results(cfg_rel, tmp)
    finally:
        tmp.unlink(missing_ok=True)

    uni = exp.get("methods_resource_unified_v1")
    assert isinstance(uni, dict)
    assert uni.get("schema") == "methods_resource_unified_v1"
    assert uni.get("run_summary_qpe_demo_track_ran") is True
    rs = uni.get("resource_summary")
    assert isinstance(rs, dict)
    assert rs.get("pauli_averaging_protocol_ran") is True
    qpeb = uni.get("qpe_demo_track")
    assert isinstance(qpeb, dict)
    assert qpeb.get("schema")
    assert uni.get("tket_first_compiled_circuit_probe_schema") == "tket_stats_attempt_v1"
    rev = exp.get("resource_estimation_preview_v1")
    assert isinstance(rev, dict)
    assert rev.get("schema") == "resource_estimation_preview_v1"
    assert rev.get("mode") == "pipeline"
    assert rev.get("resource_summary_n_circuits") is not None


def test_resource_estimation_preview_v1_config_only_export() -> None:
    env = {**os.environ, "PYTHONPATH": str(_ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", "")}
    cfg = _ROOT / "configs" / "example_h2_qpe_track_parity_integrations.yaml"
    proc = subprocess.run(
        [sys.executable, str(_ROOT / "scripts" / "export_parity_criteria_table.py"), str(cfg)],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    exp = json.loads(proc.stdout)
    rev = exp.get("resource_estimation_preview_v1")
    assert isinstance(rev, dict)
    assert rev.get("schema") == "resource_estimation_preview_v1"
    assert rev.get("mode") == "config_only"
    assert rev.get("parity_integrations_tket_first_circuit_stats") is True

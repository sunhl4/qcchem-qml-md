"""Golden parity export (config-only) + optional --results merge keys."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_FIXTURE = _ROOT / "tests" / "fixtures" / "parity_export_example_h2_config_only.json"
_RESULTS_FIXTURE = _ROOT / "tests" / "fixtures" / "pipeline_results_minimal_export_merge.json"


def _export_json(cfg_rel: str, *, results: Path | None = None) -> dict:
    env = {**os.environ, "PYTHONPATH": str(_ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", "")}
    cmd = [sys.executable, str(_ROOT / "scripts" / "export_parity_criteria_table.py"), str(_ROOT / cfg_rel)]
    if results is not None:
        cmd.extend(["--results", str(results)])
    proc = subprocess.run(cmd, cwd=str(_ROOT), capture_output=True, text=True, env=env, check=False)
    assert proc.returncode == 0, proc.stderr or proc.stdout
    return json.loads(proc.stdout)


def _normalize_export(d: dict) -> dict:
    """Normalize path separators for cross-platform comparison."""
    out = json.loads(json.dumps(d))
    sc = out.get("source_config")
    if isinstance(sc, str):
        p = Path(sc)
        if len(p.parts) >= 2 and p.parts[-2:] == ("configs", "example_h2.yaml"):
            out["source_config"] = "configs/example_h2.yaml"
        else:
            out["source_config"] = str(p).replace("\\", "/")
    return out


def test_export_example_h2_matches_golden_fixture() -> None:
    assert _FIXTURE.is_file()
    golden = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    fresh = _normalize_export(_export_json("configs/example_h2.yaml"))
    assert fresh == golden


def test_export_results_merge_includes_algorithm_sidecars() -> None:
    out = _export_json("configs/example_h2.yaml", results=_RESULTS_FIXTURE)
    assert out.get("qpe_demo_track_ran_from_run_summary") is True
    assert out.get("embedding_workflow_from_run", {}).get("mode") == "none"
    assert out.get("adapt_meta_from_run", {}).get("total_gradient_evals") == 3
    assert out.get("tensornet_engine_resolved_from_parity_snapshot") == "stub"
    assert out.get("vqd_three_protocol_present_from_run") is True
    assert out.get("qse_shot_mode_from_run_meta") == "dense_reference_only"
    assert out.get("sceom_shot_noise_model_from_run") == "none"
    assert out.get("sceom_shots_per_matrix_element_from_run") == 0


@pytest.mark.parametrize(
    "cfg_rel",
    (
        "configs/example_h2.yaml",
        "configs/tutorial_inquanto_chain_h2.yaml",
        "configs/example_h2_excited_smoke.yaml",
        "configs/example_h2_iqeb.yaml",
        "configs/example_h2_uccsd.yaml",
        "configs/example_h2_uccsd_trotter.yaml",
        "configs/example_h2_zne_circuit_fold.yaml",
        "configs/example_decomposition_plugin_toy.yaml",
        "configs/example_h2_projection_trace.yaml",
        "configs/example_h4_projection_mulliken.yaml",
        "configs/example_oniom_toy.yaml",
    ),
)
def test_m2_config_only_export_stable_keys(cfg_rel: str) -> None:
    from qchem_stack.protocols.inquanto_contract import PARITY_EXPORT_V2_STABLE_KEYS

    cfg_path = _ROOT / cfg_rel
    if not cfg_path.is_file():
        pytest.skip(f"missing {cfg_rel}")
    data = _normalize_export(_export_json(cfg_rel))
    assert not (PARITY_EXPORT_V2_STABLE_KEYS - set(data.keys()))
    assert data.get("parity_export_schema_version") == "2"


@pytest.mark.skipif(
    not Path(__file__).resolve().parents[1].joinpath("configs", "example_h2.yaml").is_file(),
    reason="configs",
)
def test_m2_pipeline_then_export_documented_keys() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = _ROOT / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    tmp = _ROOT / "tests" / "fixtures" / "_m2_tmp_pipeline_out.json"
    try:
        tmp.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        exp = _export_json("configs/example_h2.yaml", results=tmp)
        assert "parity_snapshot_from_run" in exp
        assert isinstance(exp.get("run_summary_from_repro"), dict)
    finally:
        tmp.unlink(missing_ok=True)

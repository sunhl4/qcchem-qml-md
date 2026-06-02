"""RunContext + pipeline_profile on pipeline output (strict repro JSON)."""

from __future__ import annotations

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.orchestration.run_context import RunContext
from qchem_stack.repro.export import repro_json_dumps
from tests.helpers.paths import configs_path


def _have_pyscf() -> bool:
    try:
        import pyscf  # noqa: F401

        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_run_context_appears_in_repro_and_run_summary() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rc = RunContext.new(client_request_id="client-req-xyz")
    out = run_pipeline_sync(cfg, cfg_path=configs_path("example_h2.yaml"), run_context=rc)
    rctx = out["repro"].get("run_context")
    assert isinstance(rctx, dict)
    assert rctx.get("schema") == "run_context_v1"
    assert rctx.get("trace_id") == rc.trace_id
    assert rctx.get("client_request_id") == "client-req-xyz"
    sm = out["repro"].get("run_summary", {})
    assert sm.get("trace_id") == rc.trace_id
    assert sm.get("client_request_id") == "client-req-xyz"
    repro_json_dumps(out["repro"])


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_pipeline_profile_v1_and_run_summary_slowest() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    out = run_pipeline_sync(cfg, cfg_path=configs_path("example_h2.yaml"))
    prof = out["repro"].get("pipeline_profile")
    assert isinstance(prof, dict)
    assert prof.get("schema") == "pipeline_profile_v1"
    stages = prof.get("stages")
    assert isinstance(stages, list) and len(stages) >= 3
    names = {s.get("stage") for s in stages if isinstance(s, dict)}
    assert "scf_done" in names
    assert "variational_done" in names
    assert "finalize_repro" in names
    assert "total_wall_ms" in prof
    sm = out["repro"].get("run_summary", {})
    assert "pipeline_total_wall_ms" in sm
    assert "pipeline_slowest_stage" in sm
    assert "canonical_pack_ms" in names
    assert "fermion_to_qubit_ms" in names
    cache = out.get("pre_quantum_build_cache") or {}
    assert cache.get("schema") == "run_build_cache_v1"
    assert int(cache.get("pack_builds", 0)) >= 1
    assert sm.get("pre_quantum_source") == "canonical_active_space_integral_pack"
    assert sm.get("pre_quantum_pack_builds") == int(cache.get("pack_builds", 0))
    repro_json_dumps(out["repro"])


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_pipeline_profile_memory_tracing_optional(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QCHEM_PIPELINE_PROFILE_MEM", "1")
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    out = run_pipeline_sync(cfg, cfg_path=configs_path("example_h2.yaml"))
    prof = out["repro"].get("pipeline_profile")
    assert isinstance(prof, dict)
    assert prof.get("memory_tracing_enabled") is True
    stages = prof.get("stages") or []
    assert stages and "peak_memory_kb" in stages[-1]


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_json_structured_log_emits_on_stage(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    import logging

    monkeypatch.setenv("QCHEM_STACK_JSON_LOG", "1")
    caplog.set_level(logging.INFO, logger="qchem_stack.pipeline.json")
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    run_pipeline_sync(cfg, cfg_path=configs_path("example_h2.yaml"))
    assert any("pipeline_stage" in r.message for r in caplog.records)


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_job_timeline_emit_collects_pipeline_stages() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    received: list[dict] = []

    def emit(ev: dict) -> None:
        received.append(dict(ev))

    run_pipeline_sync(cfg, cfg_path=configs_path("example_h2.yaml"), job_timeline_emit=emit)
    kinds = [e.get("kind") for e in received]
    assert "pipeline_stage" in kinds
    stages = [e.get("stage") for e in received if e.get("kind") == "pipeline_stage"]
    assert "scf_done" in stages
    assert "finalize_repro" in stages

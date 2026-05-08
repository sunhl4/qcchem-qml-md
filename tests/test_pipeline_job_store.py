"""Full-pipeline SQLite job roundtrip (requires PySCF for worker)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from qchem_stack.jobs.pipeline_jobs import enqueue_full_pipeline_run
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.jobs.worker_dispatch import dispatch_job
from qchem_stack.orchestration.run_context import RunContext


def _have_pyscf() -> bool:
    try:
        import pyscf  # noqa: F401

        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_enqueue_full_pipeline_then_dispatch_completes() -> None:
    root = Path(__file__).resolve().parents[1]
    raw = yaml.safe_load((root / "configs" / "example_h2.yaml").read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    raw.setdefault("quantum", {})["use_pauli_protocol"] = False
    raw.setdefault("quantum", {})["vqe_maxiter"] = 6
    yml = yaml.safe_dump(raw, sort_keys=False)
    with tempfile.TemporaryDirectory() as d:
        store = SqliteJobStore(f"{d}/jobs.sqlite")
        rc = RunContext.new(client_request_id="job-store-test")
        exp_id = str(raw.get("experiment_id", ""))
        h = enqueue_full_pipeline_run(
            store,
            config_yaml=yml,
            run_context=rc,
            meta_extra={"experiment_id": exp_id} if exp_id else None,
        )
        row = store.get_job_row(h.job_id)
        assert row["job_kind"] == "full_pipeline"
        assert (row.get("meta") or {}).get("experiment_id") == exp_id
        dispatch_job(store, h.job_id)
        out = store.result(h.job_id)
        assert out["status"] == "DONE"
        assert out["job_kind"] == "full_pipeline"
        assert "repro" in out
        assert out["repro"].get("run_context", {}).get("trace_id") == rc.trace_id
        assert out.get("schema") == "full_pipeline_job_result_v1"
        tl = store.get_job_timeline_events(h.job_id)
        evs = tl.get("events") or []
        assert any(
            isinstance(e, dict) and e.get("kind") == "pipeline_stage" and e.get("stage") == "scf_done"
            for e in evs
        )
        assert any(isinstance(e, dict) and e.get("kind") == "completed" for e in evs)

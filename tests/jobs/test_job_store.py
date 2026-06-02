"""Job store tests: meta filtering, retry logic, timeline tracking, and protocol flow.

Consolidates:
- test_store_experiment_meta.py
- test_job_retry.py
- test_job_timeline.py
- test_job_flow.py
"""

from __future__ import annotations

import tempfile

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.config import NexusAnalogSpec
from qchem_stack.jobs.store import (
    SqliteJobStore,
    _meta_experiment_id_from_raw,
    _meta_top_str,
    process_job_with_retry,
)
from qchem_stack.protocols.protocol import PauliAveragingProtocol


class TestMetaFilteringHelpers:
    """Helpers for job store meta filtering."""

    def test_meta_top_str(self) -> None:
        assert _meta_top_str('{"api_workspace_label": "p"}', "api_workspace_label") == "p"
        assert _meta_top_str(None, "x") is None

    def test_meta_experiment_id_from_raw(self) -> None:
        assert _meta_experiment_id_from_raw(None) is None
        assert _meta_experiment_id_from_raw("") is None
        assert _meta_experiment_id_from_raw("not json") is None
        assert _meta_experiment_id_from_raw('{"experiment_id": "z"}') == "z"
        assert _meta_experiment_id_from_raw('{"other": 1}') is None


class TestJobRetry:
    """Job retry logic."""

    def test_process_job_retry_then_fail(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            store = SqliteJobStore(f"{d}/jobs.sqlite")
            store.enqueue("bad", b"not-a-valid-pickle")
            for _ in range(3):
                process_job_with_retry(
                    store,
                    "bad",
                    PauliAveragingProtocol.process_job,
                    max_retries=2,
                )
            out = store.result("bad")
            assert out["status"] == "FAILED"
            assert out["retry_count"] >= 2
            assert out["job_kind"] == "pauli_protocol"


class TestJobTimeline:
    """Persisted job timeline (Nexus-style milestone analog)."""

    def test_timeline_submitted_then_running(self) -> None:
        from qchem_stack.jobs.pipeline_jobs import enqueue_full_pipeline_run
        from qchem_stack.orchestration.run_context import RunContext

        with tempfile.TemporaryDirectory() as d:
            path = f"{d}/tl.sqlite"
            store = SqliteJobStore(path)
            rc = RunContext.new()
            h = enqueue_full_pipeline_run(
                store,
                config_yaml="experiment_id: t1\n",
                run_context=rc,
                meta_extra={"experiment_id": "t1"},
            )
            tl0 = store.get_job_timeline_events(h.job_id)
            assert tl0["source"] == "sqlite_timeline_json_v1"
            assert len(tl0["events"]) == 1
            assert tl0["events"][0]["kind"] == "submitted"

            store.mark_running(h.job_id)
            tl1 = store.get_job_timeline_events(h.job_id)
            assert len(tl1["events"]) == 2
            assert tl1["events"][-1]["kind"] == "running"


class TestProtocolJobFlow:
    """Full protocol job lifecycle: launch, process, retrieve."""

    def test_launch_process_retrieve(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            store = SqliteJobStore(f"{d}/jobs.sqlite")
            h = QubitOperator(((0, "Z"),), 0.5) + QubitOperator((), 0.0)
            na = NexusAnalogSpec(enabled=True, project_label="async_parity", unit_per_shot=0.5)
            proto = PauliAveragingProtocol(
                hamiltonian=h,
                n_qubits=1,
                backend=BackendSpec(name="sim", shots_per_circuit=10),
                pass_bundle=CompilerPassBundle(),
                nexus_analog=na,
            )
            proto.instantiate()
            proto.build(np.array([0.1, 0.2]), hea_depth=1)
            handle = proto.launch(store)
            assert handle.protocol_hash is not None and len(handle.protocol_hash) == 32
            PauliAveragingProtocol.process_job(store, handle.job_id)
            out = proto.retrieve(store, handle)
            assert out.get("status") == "DONE"
            assert "expectation" in out
            bill = out.get("nexus_analog_billing")
            assert isinstance(bill, dict)
            assert bill.get("project_label") == "async_parity"

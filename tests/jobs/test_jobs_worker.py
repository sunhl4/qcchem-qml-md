from __future__ import annotations

import tempfile
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.jobs.worker import drain_one_queued
from qchem_stack.protocols.protocol import PauliAveragingProtocol


def test_drain_one_queued_runs_job() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/jobs.sqlite"
        store = SqliteJobStore(path)
        h = QubitOperator(((0, "Z"),), 0.5) + QubitOperator((), 0.0)
        proto = PauliAveragingProtocol(
            hamiltonian=h,
            n_qubits=1,
            backend=BackendSpec(name="sim", shots_per_circuit=8),
            pass_bundle=CompilerPassBundle(),
        )
        proto.instantiate()
        proto.build(np.array([0.1, 0.2]), hea_depth=1)
        handle = proto.launch(store)
        assert drain_one_queued(store, PauliAveragingProtocol.process_job)
        out = store.result(handle.job_id)
        assert out["status"] == "DONE"
        assert out["job_kind"] == "pauli_protocol"
        assert "expectation" in out


def test_claim_next_queued_is_atomic_between_workers() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/jobs.sqlite"
        store = SqliteJobStore(path)
        store.enqueue("j-1", b"payload")

        def _claim_one() -> str | None:
            return store.claim_next_queued()

        with ThreadPoolExecutor(max_workers=2) as ex:
            claimed = [f.result() for f in [ex.submit(_claim_one), ex.submit(_claim_one)]]

        assert claimed.count("j-1") == 1
        assert claimed.count(None) == 1
        assert store.result("j-1")["status"] == "RUNNING"


def test_two_workers_drain_distinct_jobs() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/jobs.sqlite"
        store = SqliteJobStore(path)
        for i in range(4):
            store.enqueue(f"j-{i}", f"payload-{i}".encode())

        def _drain_one() -> str | None:
            jid = store.claim_next_queued()
            if jid is None:
                return None
            store.complete(jid, {"ok": True})
            return jid

        with ThreadPoolExecutor(max_workers=2) as ex:
            claimed = [f.result() for f in [ex.submit(_drain_one) for _ in range(4)]]

        assert len({c for c in claimed if c is not None}) == 4
        assert claimed.count(None) == 0


def test_worker_max_retries_exhausted() -> None:
    from qchem_stack.jobs.store import process_job_with_retry

    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/jobs.sqlite"
        store = SqliteJobStore(path)
        store.enqueue("fail-job", b"payload")
        store.claim_next_queued()

        def _always_fail(_store: SqliteJobStore, _jid: str) -> None:
            raise RuntimeError("boom")

        process_job_with_retry(store, "fail-job", _always_fail, max_retries=2, already_running=True)
        for _ in range(2):
            store.claim_next_queued()
            process_job_with_retry(
                store, "fail-job", _always_fail, max_retries=2, already_running=True
            )
        row = store.result("fail-job")
        assert row["status"] == "FAILED"
        assert row["retry_count"] >= 2

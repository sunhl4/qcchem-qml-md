from __future__ import annotations

import tempfile

from qchem_stack.jobs.store import SqliteJobStore, process_job_with_retry
from qchem_stack.protocols.protocol import PauliAveragingProtocol


def test_process_job_retry_then_fail() -> None:
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

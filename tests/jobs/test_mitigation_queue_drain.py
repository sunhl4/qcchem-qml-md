"""E2E drain for local mitigation async queue (P1-R01 evidence)."""

from __future__ import annotations

import asyncio

from qchem_stack.jobs.mitigation_queue import LocalMitigationJobQueue


def test_mitigation_queue_drain_all_e2e() -> None:
    queue = LocalMitigationJobQueue()

    def handler(payload: dict) -> dict:
        return {"mitigation_trace": "qermit_runtime_v1", "scale": payload.get("scale", 1)}

    queue.submit("job-1", {"scale": 1})
    queue.submit("job-2", {"scale": 3})

    done = asyncio.run(queue.drain_all(handler, concurrency=2))
    assert len(done) == 2
    assert all(j.status == "done" for j in done)
    assert all(j.result and j.result.get("mitigation_trace") == "qermit_runtime_v1" for j in done)

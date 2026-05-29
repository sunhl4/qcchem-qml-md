"""Local async mitigation job queue (open-stack analog, not Nexus MitEx)."""

from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MitigationJob:
    job_id: str
    payload: dict[str, Any]
    status: str = "pending"
    result: dict[str, Any] | None = None


@dataclass
class LocalMitigationJobQueue:
    """In-process FIFO queue for mitigation DAG batches."""

    _pending: deque[MitigationJob] = field(default_factory=deque)
    _completed: list[MitigationJob] = field(default_factory=list)

    def submit(self, job_id: str, payload: dict[str, Any]) -> MitigationJob:
        job = MitigationJob(job_id=job_id, payload=dict(payload))
        self._pending.append(job)
        return job

    async def drain_once(self, handler) -> list[MitigationJob]:
        if not self._pending:
            return []
        job = self._pending.popleft()
        job.status = "running"
        job.result = await asyncio.to_thread(handler, job.payload)
        job.status = "done"
        self._completed.append(job)
        return [job]

    def stats(self) -> dict[str, int]:
        return {
            "pending": len(self._pending),
            "completed": len(self._completed),
        }

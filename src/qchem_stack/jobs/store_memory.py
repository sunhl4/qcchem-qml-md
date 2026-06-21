"""In-process job store for tests and single-worker dev (no persistence)."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from .store_retry import exponential_backoff_delay
from .store_schema import (
    DEFAULT_JOB_KIND,
    JobHandle,
    JobPublicSummary,
    JobStatus,
    parse_meta_json,
)
from .store_sql import dump_timeline_events, load_timeline_events


@dataclass
class _MemoryJobRow:
    payload: bytes
    status: str = JobStatus.QUEUED.value
    result: str | None = None
    created: float = field(default_factory=time.time)
    updated: float = field(default_factory=time.time)
    retry_count: int = 0
    error_message: str | None = None
    protocol_hash: str | None = None
    job_kind: str = DEFAULT_JOB_KIND
    meta: str | None = None
    timeline_json: str | None = None


class InMemoryJobStore:
    """Thread-safe dict-backed :class:`~qchem_stack.jobs.store_schema.WorkerJobStore`."""

    def __init__(self) -> None:
        self._rows: dict[str, _MemoryJobRow] = {}
        self._lock = threading.Lock()

    def enqueue(
        self,
        job_id: str,
        payload: bytes,
        protocol_hash: str | None = None,
        *,
        job_kind: str = DEFAULT_JOB_KIND,
        meta: dict[str, Any] | None = None,
    ) -> JobHandle:
        now = time.time()
        meta_s = json.dumps(meta, sort_keys=True) if meta is not None else None
        timeline = dump_timeline_events(
            [{"t": now, "kind": "submitted", "status": JobStatus.QUEUED.value}]
        )
        with self._lock:
            self._rows[job_id] = _MemoryJobRow(
                payload=payload,
                created=now,
                updated=now,
                protocol_hash=protocol_hash,
                job_kind=job_kind,
                meta=meta_s,
                timeline_json=timeline,
            )
        return JobHandle(job_id=job_id, protocol_hash=protocol_hash)

    def claim_next_queued(self) -> str | None:
        with self._lock:
            candidates = [
                (jid, row)
                for jid, row in self._rows.items()
                if row.status == JobStatus.QUEUED.value and row.updated <= time.time()
            ]
            if not candidates:
                return None
            job_id, row = min(candidates, key=lambda item: item[1].created)
            row.status = JobStatus.RUNNING.value
            row.updated = time.time()
        self.append_timeline(job_id, "running", JobStatus.RUNNING.value)
        return job_id

    def mark_running(self, job_id: str) -> None:
        with self._lock:
            row = self._require(job_id)
            row.status = JobStatus.RUNNING.value
            row.updated = time.time()
        self.append_timeline(job_id, "running", JobStatus.RUNNING.value)

    def complete(self, job_id: str, result: dict[str, Any]) -> None:
        with self._lock:
            row = self._require(job_id)
            row.status = JobStatus.DONE.value
            row.result = json.dumps(result)
            row.error_message = None
            row.updated = time.time()
        self.append_timeline(job_id, "completed", JobStatus.DONE.value)

    def fail(self, job_id: str, message: str) -> None:
        with self._lock:
            row = self._require(job_id)
            row.status = JobStatus.FAILED.value
            row.error_message = message[:8000]
            row.updated = time.time()
        self.append_timeline(job_id, "failed", JobStatus.FAILED.value)

    def mark_timed_out(self, job_id: str, timeout_seconds: int) -> None:
        message = f"Job exceeded timeout limit of {timeout_seconds} seconds"
        self.fail(job_id, message)
        with self._lock:
            self._require(job_id).status = JobStatus.TIMED_OUT.value
        self.append_timeline(job_id, "timed_out", JobStatus.TIMED_OUT.value)

    def append_timeline_event(self, job_id: str, event: dict[str, Any]) -> None:
        with self._lock:
            row = self._require(job_id)
            events = load_timeline_events(row.timeline_json)
            entry = dict(event)
            if "t" not in entry:
                entry["t"] = time.time()
            events.append(entry)
            row.timeline_json = dump_timeline_events(events)

    def append_timeline(self, job_id: str, kind: str, status: str) -> None:
        self.append_timeline_event(job_id, {"kind": kind, "status": status})

    def result(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            row = self._require(job_id)
            out: dict[str, Any] = {
                "status": row.status,
                "retry_count": row.retry_count,
                "job_kind": row.job_kind,
            }
            meta_obj = parse_meta_json(row.meta)
            if meta_obj is not None:
                out["meta"] = meta_obj
            if row.error_message:
                out["error"] = row.error_message
            if row.status == JobStatus.DONE.value and row.result is not None:
                out.update(json.loads(row.result))
            return out

    def get_job_public_summary(self, job_id: str) -> JobPublicSummary:
        with self._lock:
            row = self._require(job_id)
            out: JobPublicSummary = {
                "job_id": job_id,
                "status": row.status,
                "job_kind": row.job_kind,
                "created": row.created,
                "updated": row.updated,
                "retry_count": row.retry_count,
            }
            meta_obj = parse_meta_json(row.meta)
            if meta_obj is not None:
                out["meta"] = meta_obj
            if row.error_message:
                out["error"] = row.error_message[:2000]
            return out

    def get_job_row(self, job_id: str) -> dict[str, Any]:
        with self._lock:
            row = self._require(job_id)
            return {
                "payload": row.payload,
                "job_kind": row.job_kind,
                "meta": parse_meta_json(row.meta),
                "protocol_hash": row.protocol_hash,
                "status": row.status,
            }

    def requeue_after_failure(
        self,
        job_id: str,
        message: str,
        *,
        max_retries: int,
        exponential_backoff: bool = False,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ) -> bool:
        with self._lock:
            row = self._require(job_id)
            if row.retry_count < max_retries:
                row.retry_count += 1
                row.status = JobStatus.QUEUED.value
                row.error_message = message[:8000]
                if exponential_backoff:
                    delay = exponential_backoff_delay(row.retry_count - 1, base_delay, max_delay)
                    row.updated = time.time() + delay
                else:
                    row.updated = time.time()
                scheduled = True
            else:
                row.status = JobStatus.FAILED.value
                row.error_message = message[:8000]
                row.updated = time.time()
                scheduled = False
        if scheduled:
            self.append_timeline(job_id, "retry_scheduled", JobStatus.QUEUED.value)
        else:
            self.append_timeline(job_id, "failed", JobStatus.FAILED.value)
        return scheduled

    def _require(self, job_id: str) -> _MemoryJobRow:
        row = self._rows.get(job_id)
        if row is None:
            raise KeyError(job_id)
        return row

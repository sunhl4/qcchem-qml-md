"""Job store timeline append/read helpers (mixin for :class:`~qchem_stack.jobs.store_service.SqliteJobStore`)."""

from __future__ import annotations

import time
from typing import Any

from qchem_stack.contracts.schema_ids import JOB_TIMELINE_V1

from .store_schema import JobStatus, JobStoreSqlProtocol, JobTimelineResponse
from .store_sql import dump_timeline_events, load_timeline_events


class JobStoreTimelineMixin:
    """Timeline JSON column operations."""

    def append_timeline_event(
        self: JobStoreSqlProtocol, job_id: str, event: dict[str, Any]
    ) -> None:
        con = self._connect()
        row = con.execute("SELECT timeline_json FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if row is None:
            con.close()
            raise KeyError(job_id)
        events = load_timeline_events(row[0])
        entry = dict(event)
        if "t" not in entry:
            entry["t"] = time.time()
        events.append(entry)
        con.execute(
            "UPDATE jobs SET timeline_json=? WHERE job_id=?",
            (dump_timeline_events(events), job_id),
        )
        con.commit()
        con.close()

    def append_timeline(self: JobStoreSqlProtocol, job_id: str, kind: str, status: str) -> None:
        self.append_timeline_event(job_id, {"kind": kind, "status": status})

    def get_job_timeline_events(self: JobStoreSqlProtocol, job_id: str) -> JobTimelineResponse:
        con = self._connect()
        row = con.execute(
            "SELECT timeline_json, created, updated, status FROM jobs WHERE job_id=?",
            (job_id,),
        ).fetchone()
        con.close()
        if row is None:
            raise KeyError(job_id)
        raw, created, updated, status = row
        events = load_timeline_events(raw)
        if events:
            return {
                "schema": JOB_TIMELINE_V1,
                "source": "sqlite_timeline_json_v1",
                "events": events,
            }
        return {
            "schema": JOB_TIMELINE_V1,
            "source": "sqlite_coarse_timeline_v1",
            "events": [
                {
                    "t": float(created) if created is not None else 0.0,
                    "kind": "submitted",
                    "status": JobStatus.QUEUED.value,
                },
                {
                    "t": float(updated) if updated is not None else 0.0,
                    "kind": "state_snapshot",
                    "status": str(status),
                },
            ],
        }

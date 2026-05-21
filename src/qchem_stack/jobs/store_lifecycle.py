"""Job status transitions, claim, and result fetch (mixin)."""

from __future__ import annotations

import json
import time
from typing import Any

from .store_schema import (
    DEFAULT_JOB_KIND,
    JobPublicSummary,
    JobStatus,
    JobStoreSqlProtocol,
    parse_meta_json,
)


class JobStoreLifecycleMixin:
    """RUNNING / DONE / FAILED transitions and row reads."""

    def mark_running(self: JobStoreSqlProtocol, job_id: str) -> None:
        con = self._connect()
        con.execute(
            "UPDATE jobs SET status=?, updated=? WHERE job_id=?",
            (JobStatus.RUNNING.value, time.time(), job_id),
        )
        con.commit()
        con.close()
        self.append_timeline(job_id, "running", JobStatus.RUNNING.value)

    def complete(self: JobStoreSqlProtocol, job_id: str, result: dict[str, Any]) -> None:
        con = self._connect()
        con.execute(
            "UPDATE jobs SET status=?, result=?, error_message=NULL, updated=? WHERE job_id=?",
            (JobStatus.DONE.value, json.dumps(result), time.time(), job_id),
        )
        con.commit()
        con.close()
        self.append_timeline(job_id, "completed", JobStatus.DONE.value)

    def fail(self: JobStoreSqlProtocol, job_id: str, message: str) -> None:
        con = self._connect()
        con.execute(
            "UPDATE jobs SET status=?, error_message=?, updated=? WHERE job_id=?",
            (JobStatus.FAILED.value, message[:8000], time.time(), job_id),
        )
        con.commit()
        con.close()
        self.append_timeline(job_id, "failed", JobStatus.FAILED.value)

    def fetch_next_queued(self: JobStoreSqlProtocol) -> str | None:
        con = self._connect()
        row = con.execute(
            "SELECT job_id FROM jobs WHERE status=? ORDER BY created ASC LIMIT 1",
            (JobStatus.QUEUED.value,),
        ).fetchone()
        con.close()
        return str(row[0]) if row else None

    def claim_next_queued(self: JobStoreSqlProtocol) -> str | None:
        con = self._connect()
        now = time.time()
        job_id: str | None = None
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT job_id FROM jobs WHERE status=? ORDER BY created ASC LIMIT 1",
                (JobStatus.QUEUED.value,),
            ).fetchone()
            if row is None:
                con.commit()
                return None
            job_id = str(row[0])
            con.execute(
                "UPDATE jobs SET status=?, updated=? WHERE job_id=?",
                (JobStatus.RUNNING.value, now, job_id),
            )
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
        if job_id is not None:
            self.append_timeline(job_id, "running", JobStatus.RUNNING.value)
        return job_id

    def result(self: JobStoreSqlProtocol, job_id: str) -> dict[str, Any]:
        con = self._connect()
        row = con.execute(
            """SELECT status, result, error_message, retry_count, job_kind, meta
               FROM jobs WHERE job_id=?""",
            (job_id,),
        ).fetchone()
        con.close()
        if row is None:
            raise KeyError(job_id)
        status, res, err, retries, job_kind, meta_raw = row
        out: dict[str, Any] = {
            "status": status,
            "retry_count": int(retries or 0),
            "job_kind": job_kind or DEFAULT_JOB_KIND,
        }
        meta_obj = parse_meta_json(meta_raw)
        if meta_obj is not None:
            out["meta"] = meta_obj
        if err:
            out["error"] = err
        if status == JobStatus.DONE.value and res is not None:
            out.update(json.loads(res))
        return out

    def get_job_public_summary(self: JobStoreSqlProtocol, job_id: str) -> JobPublicSummary:
        con = self._connect()
        row = con.execute(
            """SELECT status, job_kind, created, updated, meta, retry_count, error_message
               FROM jobs WHERE job_id=?""",
            (job_id,),
        ).fetchone()
        con.close()
        if row is None:
            raise KeyError(job_id)
        st, jk, created, updated, meta_raw, retries, err = row
        out: JobPublicSummary = {
            "job_id": job_id,
            "status": str(st),
            "job_kind": jk or DEFAULT_JOB_KIND,
            "created": float(created) if created is not None else None,
            "updated": float(updated) if updated is not None else None,
            "retry_count": int(retries or 0),
        }
        meta_obj = parse_meta_json(meta_raw)
        if meta_obj is not None:
            out["meta"] = meta_obj
        if err:
            out["error"] = str(err)[:2000]
        return out

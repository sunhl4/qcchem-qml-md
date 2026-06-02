"""Job store types, protocols, and JSON/meta helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, TypedDict

if TYPE_CHECKING:
    import sqlite3


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


DEFAULT_JOB_KIND = "pauli_protocol"


@dataclass
class JobHandle:
    job_id: str
    protocol_hash: str | None = None
    """SHA-256 digest (hex prefix) of pickled protocol; matches DB ``jobs.protocol_hash`` when set."""


class JobTimelineEvent(TypedDict, total=False):
    t: float
    kind: str
    status: str


class JobTimelineResponse(TypedDict):
    schema: str
    source: str
    events: list[JobTimelineEvent]


class JobListItem(TypedDict, total=False):
    job_id: str
    status: str
    job_kind: str
    created: float | None
    updated: float | None
    protocol_hash: str
    meta: dict[str, Any] | None


class JobStoreSqlProtocol(Protocol):
    """Methods provided by :class:`~qchem_stack.jobs.store_service.SqliteJobStore` for mixins."""

    def _connect(self) -> sqlite3.Connection: ...

    def append_timeline_event(self, job_id: str, event: dict[str, Any]) -> None: ...

    def append_timeline(self, job_id: str, kind: str, status: str) -> None: ...


class JobPublicSummary(TypedDict, total=False):
    job_id: str
    status: str
    job_kind: str
    created: float | None
    updated: float | None
    retry_count: int
    meta: dict[str, Any]
    error: str


class JobStore(Protocol):
    def enqueue(
        self, job_id: str, payload: bytes, protocol_hash: str | None = None
    ) -> JobHandle: ...

    def result(self, job_id: str) -> dict[str, Any]: ...


def parse_meta_json(meta_raw: str | None) -> dict[str, Any] | None:
    if not meta_raw:
        return None
    try:
        parsed = json.loads(meta_raw)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def meta_top_str(meta_raw: str | None, key: str) -> str | None:
    if not meta_raw or not key:
        return None
    obj = parse_meta_json(meta_raw)
    if obj is None:
        return None
    v = obj.get(key)
    return str(v) if v is not None else None


def meta_experiment_id_from_raw(meta_raw: str | None) -> str | None:
    return meta_top_str(meta_raw, "experiment_id")

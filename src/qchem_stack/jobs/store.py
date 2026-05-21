"""Job store public API (facade over schema + SQL + service modules)."""

from __future__ import annotations

from .store_schema import (
    JobHandle,
    JobStatus,
    JobStore,
    meta_experiment_id_from_raw,
    meta_top_str,
)
from .store_service import SqliteJobStore, process_job_with_retry

# Backward-compatible private aliases used by tests.
_meta_top_str = meta_top_str
_meta_experiment_id_from_raw = meta_experiment_id_from_raw

__all__ = [
    "JobHandle",
    "JobStatus",
    "JobStore",
    "SqliteJobStore",
    "process_job_with_retry",
    "_meta_top_str",
    "_meta_experiment_id_from_raw",
]

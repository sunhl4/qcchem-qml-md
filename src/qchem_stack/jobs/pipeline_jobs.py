"""Enqueue full-pipeline runs on :class:`SqliteJobStore` (async worker-friendly)."""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING, Any

from qchem_stack.jobs.kinds import JOB_KIND_FULL_PIPELINE
from qchem_stack.jobs.store import JobHandle, SqliteJobStore

if TYPE_CHECKING:
    from qchem_stack.orchestration.run_context import RunContext


def enqueue_full_pipeline_run(
    store: SqliteJobStore,
    *,
    config_yaml: str,
    run_context: RunContext | None = None,
    meta_extra: dict[str, Any] | None = None,
) -> JobHandle:
    """Queue YAML experiment; worker runs :func:`~qchem_stack.orchestration.pipeline.run_pipeline_sync`.

    ``meta_extra`` is merged into the store ``meta`` JSON (e.g. ``experiment_id``, labels for list filters).
    """
    job_id = str(uuid.uuid4())
    body: dict = {"config_yaml": config_yaml}
    if run_context is not None:
        body["run_context"] = run_context.to_repro_dict()
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    meta: dict[str, Any] = {}
    if run_context is not None:
        meta["trace_id"] = run_context.trace_id
    if meta_extra:
        meta.update(meta_extra)
    meta_arg: dict[str, Any] | None = meta if meta else None
    return store.enqueue(
        job_id,
        payload,
        job_kind=JOB_KIND_FULL_PIPELINE,
        meta=meta_arg,
    )

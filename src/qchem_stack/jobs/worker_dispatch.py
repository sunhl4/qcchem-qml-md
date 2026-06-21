"""Route SQLite jobs to Pauli protocol pickle or full-pipeline YAML runner."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.jobs.kinds import JOB_KIND_FULL_PIPELINE

if TYPE_CHECKING:
    from qchem_stack.jobs.store_schema import WorkerJobStore


def dispatch_job(store: WorkerJobStore, job_id: str) -> None:
    row = store.get_job_row(job_id)
    if row.get("job_kind") == JOB_KIND_FULL_PIPELINE:
        from qchem_stack.jobs.pipeline_runner import run_full_pipeline_job

        run_full_pipeline_job(store, job_id)
    else:
        from qchem_stack.protocols.protocol import PauliAveragingProtocol

        PauliAveragingProtocol.process_job(store, job_id)

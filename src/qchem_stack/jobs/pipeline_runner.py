"""SQLite worker entry: deserialize full-pipeline job and persist JSON-safe result."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from qchem_stack.config import ExperimentConfig
from qchem_stack.config.path_sandbox import ConfigBaseDirError, validate_config_base_dir
from qchem_stack.contracts.schema_ids import FULL_PIPELINE_JOB_RESULT_V1
from qchem_stack.exceptions import JobPayloadError
from qchem_stack.jobs.kinds import JOB_KIND_FULL_PIPELINE
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.orchestration.run_context import RunContext

if TYPE_CHECKING:
    from qchem_stack.jobs.store_schema import WorkerJobStore
    from qchem_stack.orchestration.pipeline_result import PipelineResultV1

_RESULT_KEYS = (
    "repro",
    "scf_energy",
    "energy_after_variational",
    "energy_pauli_protocol",
    "hamiltonian_meta",
    "embedding_workflow",
    "algorithm",
    "nfev",
    "adapt_meta",
    "adapt_pool",
    "iqeb_meta",
    "iqeb_selected_pauli_strings",
    "iqcc_meta",
    "iqcc_selected_generators",
    "resource_summary",
    "protocol_counts",
    "vqe_meta",
    "angles",
    "job",
    "job_result",
    "schmidt_per_fragment_vqe",
    "vqd",
    "qse",
    "sceom",
    "excited_resource_summary",
    # Nexus / mitigation / parity-shaped sidecars (same keys as sync ``run_pipeline_sync``)
    "nexus_analog_ledger",
    "mitigation_graph_report",
    "mitigation_dag_execution",
    "nexus_cloud_repro",
    "tensornet_protocol_stub",
    "qpe_demo_track",
    "vqs_track",
)


def pipeline_result_for_job_store(out: PipelineResultV1) -> dict[str, Any]:
    """Drop large redundant fields (e.g. shot rows) while keeping reproducibility core."""
    payload = dict(out)
    slim: dict[str, Any] = {k: payload[k] for k in _RESULT_KEYS if k in payload}
    slim["schema"] = FULL_PIPELINE_JOB_RESULT_V1
    return slim


def run_full_pipeline_job(store: WorkerJobStore, job_id: str) -> None:
    row = store.get_job_row(job_id)
    kind = row.get("job_kind") or "pauli_protocol"
    if kind != JOB_KIND_FULL_PIPELINE:
        raise JobPayloadError(
            f"job {job_id}: expected job_kind {JOB_KIND_FULL_PIPELINE!r}, got {kind!r}"
        )
    raw = row["payload"]
    if not isinstance(raw, bytes):
        raise JobPayloadError("payload must be bytes")
    body = json.loads(raw.decode("utf-8"))
    cy = body.get("config_yaml")
    if not isinstance(cy, str) or not cy.strip():
        raise JobPayloadError("full_pipeline payload missing config_yaml")
    data = yaml.safe_load(cy)
    if not isinstance(data, dict):
        raise JobPayloadError("config_yaml must parse to a mapping")
    base_dir_raw = body.get("config_base_dir")
    base_dir: Path | None = None
    if base_dir_raw is not None:
        if not isinstance(base_dir_raw, str) or not base_dir_raw.strip():
            raise JobPayloadError("config_base_dir must be a non-empty string when provided")
        try:
            base_dir = validate_config_base_dir(base_dir_raw)
        except ConfigBaseDirError as exc:
            raise JobPayloadError(str(exc)) from exc
    cfg = ExperimentConfig.from_yaml_dict(
        data,
        geometry_files_base_dir=base_dir,
    )
    rc = None
    rcd = body.get("run_context")
    if isinstance(rcd, dict) and rcd.get("trace_id"):
        rc = RunContext(
            trace_id=str(rcd["trace_id"]),
            client_request_id=rcd.get("client_request_id"),
        )
    out = run_pipeline_sync(
        cfg,
        cfg_path=None,
        run_context=rc,
        job_timeline_emit=lambda e: store.append_timeline_event(job_id, e),
    )
    slim = pipeline_result_for_job_store(out)
    meta_raw = row.get("meta")
    if isinstance(meta_raw, str) and meta_raw.strip():
        try:
            meta = json.loads(meta_raw)
        except json.JSONDecodeError:
            meta = {}
    elif isinstance(meta_raw, dict):
        meta = meta_raw
    else:
        meta = {}
    if isinstance(slim.get("repro"), dict):
        rs = slim["repro"].setdefault("run_summary", {})
        if not isinstance(rs, dict):
            rs = {}
            slim["repro"]["run_summary"] = rs
        for key in ("api_workspace_label", "api_project_slug", "experiment_id"):
            if meta.get(key) is not None:
                rs[key] = meta[key]
    store.complete(job_id, slim)

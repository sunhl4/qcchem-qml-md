"""HTTP request/response models for the qchem-stack API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    experiment_yaml: str = Field(..., description="Full experiment YAML (same as CLI configs)")
    sync: bool = Field(
        default=False,
        description=(
            "If true, run in-process and return full_pipeline_job_result_v1 "
            "(JSON-safe slim dict, same as async DONE payload)"
        ),
    )
    job_db_path: str | None = Field(
        default=None, description="SQLite path for queued jobs; default from QCHEM_JOB_DB or temp"
    )
    workspace_label: str | None = Field(
        default=None,
        description="Optional Nexus-style project/workspace string stored in job meta (api_workspace_label)",
    )
    project_slug: str | None = Field(
        default=None,
        description=(
            "Optional Nexus/organization project slug stored in meta (api_project_slug); "
            "pairs with workspace for listing"
        ),
    )
    config_base_dir: str | None = Field(
        default=None,
        description=(
            "Optional base directory for resolving relative geometry_file/precomputed paths "
            "in experiment_yaml"
        ),
    )


class YamlPreviewBody(BaseModel):
    experiment_yaml: str = Field(
        ..., description="YAML to validate; returns computable list without running chemistry"
    )
    include_computables_rich: bool = Field(
        default=False,
        description=(
            "Optional parallel field: adds computables_rich (schema computables_rich_v1) "
            "without removing computable_abstract"
        ),
    )


class QMEFValidateBody(BaseModel):
    qmef: dict[str, Any] = Field(
        ..., description="JSON object matching QMEFDataset (frames + optional provenance_yaml)"
    )


class QMEFTrainerStubFitBody(BaseModel):
    qmef: dict[str, Any] = Field(..., description="Validated QMEFDataset JSON")
    hyperparams: dict[str, Any] = Field(
        default_factory=dict, description="Forwarded into StubTorchMLIPTrainer.fit meta"
    )

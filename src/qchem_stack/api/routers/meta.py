from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query, Request

from qchem_stack.api.deps import (
    default_job_db_path,
    experiment_config_from_request_yaml,
    sqlite_job_store,
)
from qchem_stack.api.middleware import META_POST_LIMIT, rate_limit
from qchem_stack.api.models import YamlPreviewBody
from qchem_stack.contracts.schema_ids import (
    CAPABILITY_GAP_EXPORT_V1,
    CAPABILITY_SURFACE_V2,
    COMPUTABLES_PREVIEW_V1,
    PRODUCT_SURFACE_V1,
    QUEUE_STATS_V1,
)
from qchem_stack.integrations.workflow_preview import workflow_preview_payload
from qchem_stack.protocols.computable import computables_export_dict, list_computables_for_config

router = APIRouter(tags=["meta", "product"])


@router.get("/v1/meta/product-surface", tags=["product"])
def product_surface() -> dict[str, object]:
    from qchem_stack import __version__

    return {
        "schema": PRODUCT_SURFACE_V1,
        "qchem_stack_version": __version__,
        "capability_notes": [
            "Five-stage protocol preview: POST /v1/meta/workflow-preview (YAML-only, no chemistry).",
            "Computable DAG (semantic v2): POST /v1/meta/workflow-preview.",
            "Capability one-shot: GET /v1/meta/capability-surface (product capability map + product gaps + operator_pool_registry_export_v1).",
            "Job lifecycle: POST/GET /v1/runs (optional project_slug), GET /v1/runs/{id}/summary, repro GET /v1/runs/{id}/repro (DONE only); events use persisted timeline when available.",
            "ML / MD bridge surface: GET /v1/meta/ml-md-bridge; validate QMEFDataset JSON: POST /v1/meta/qmef-validate; in-memory MLIP stub fit: POST /v1/meta/ml-md-trainer-stub-fit.",
        ],
        "gap_export": "/v1/meta/parity-gaps",
        "capability_surface": "/v1/meta/capability-surface",
        "ml_md_bridge": "/v1/meta/ml-md-bridge",
    }


@router.get("/v1/meta/capability-surface")
def capability_surface() -> dict[str, object]:
    from qchem_stack import __version__
    from qchem_stack.protocols.product_contract import (
        ansatz_protocol_matrix_v1,
        mitigation_execution_model_public,
        open_stack_differentiators_public,
        product_capability_map_for_docs,
        product_gap_anchor_index_v1,
        product_gap_categories,
        validate_product_gap_categories,
    )
    from qchem_stack.quantum.algorithm_registry import algorithm_registry_export
    from qchem_stack.quantum.algorithms.uccsd_vqe import uccsd_mapping_support_matrix_v1
    from qchem_stack.quantum.excited_plugins.registry import excited_registry_export
    from qchem_stack.quantum.operator_pool_registry import operator_pool_registry_export_v1
    from qchem_stack.quantum.variational_plugins.registry import variational_registry_export

    errs = validate_product_gap_categories()
    if errs:
        raise HTTPException(
            status_code=500,
            detail={"message": "invalid product_gap_categories contract", "errors": errs},
        )
    return {
        "schema": CAPABILITY_SURFACE_V2,
        "qchem_stack_version": __version__,
        "capability_map": product_capability_map_for_docs(),
        "gaps": product_gap_categories(),
        "gap_anchor_index_v1": product_gap_anchor_index_v1(),
        "mitigation_execution_model": mitigation_execution_model_public(),
        "open_stack_differentiators": open_stack_differentiators_public(),
        "operator_pool_registry_export_v1": operator_pool_registry_export_v1(),
        "algorithm_registry_export_v1": algorithm_registry_export(),
        "variational_registry_export_v1": variational_registry_export(),
        "excited_registry_export_v1": excited_registry_export(),
        "uccsd_mapping_support_matrix_v1": uccsd_mapping_support_matrix_v1(),
        "ansatz_protocol_matrix_v1": ansatz_protocol_matrix_v1(),
    }


@router.get("/v1/meta/parity-gaps")
def parity_gaps() -> dict[str, object]:
    from qchem_stack import __version__
    from qchem_stack.protocols.product_contract import (
        product_gap_anchor_index_v1,
        product_gap_categories,
        validate_product_gap_categories,
    )

    errs = validate_product_gap_categories()
    if errs:
        raise HTTPException(
            status_code=500,
            detail={"message": "invalid product_gap_categories contract", "errors": errs},
        )
    return {
        "schema": CAPABILITY_GAP_EXPORT_V1,
        "qchem_stack_version": __version__,
        "gaps": product_gap_categories(),
        "gap_anchor_index_v1": product_gap_anchor_index_v1(),
    }


@router.post("/v1/meta/workflow-preview", tags=["product"])
@rate_limit(META_POST_LIMIT)
def workflow_preview(
    request: Request, body: Annotated[YamlPreviewBody, Body()]
) -> dict[str, object]:
    cfg = experiment_config_from_request_yaml(body.experiment_yaml)
    return workflow_preview_payload(cfg, include_computables_rich=body.include_computables_rich)


@router.post("/v1/meta/computables-preview")
@rate_limit(META_POST_LIMIT)
def computables_preview(
    request: Request, body: Annotated[YamlPreviewBody, Body()]
) -> dict[str, object]:
    cfg = experiment_config_from_request_yaml(body.experiment_yaml)
    refs = list_computables_for_config(cfg)
    return {
        "schema": COMPUTABLES_PREVIEW_V1,
        "experiment_id": cfg.experiment_id,
        "computables": [{"name": r.name, "kind": r.kind, "details": r.details} for r in refs],
        "computable_abstract": computables_export_dict(cfg, protocol_counts=None),
    }


@router.get("/v1/meta/queue-stats")
def queue_stats(
    job_db_path: str | None = Query(
        default=None, description="SQLite path; default QCHEM_JOB_DB or temp"
    ),
) -> dict[str, object]:
    db = Path(job_db_path) if job_db_path else default_job_db_path()
    store = sqlite_job_store(str(db))
    return {
        "schema": QUEUE_STATS_V1,
        "job_db": str(store.path.resolve()),
        "counts": store.count_by_status(),
    }

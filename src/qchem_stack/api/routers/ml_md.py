from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from qchem_stack.md_bridge.http_surface import (
    ml_md_bridge_surface_v1,
    qmef_validate_response_dict,
    trainer_stub_fit_response_dict,
    validate_qmef_dict,
)

if TYPE_CHECKING:
    from qchem_stack.api.models import QMEFTrainerStubFitBody, QMEFValidateBody

router = APIRouter(tags=["ml_md"])


@router.get("/v1/meta/ml-md-bridge")
def ml_md_bridge_meta() -> dict[str, object]:
    return ml_md_bridge_surface_v1()


@router.post("/v1/meta/qmef-validate")
def qmef_validate(body: QMEFValidateBody) -> dict[str, object]:
    try:
        ds = validate_qmef_dict(body.qmef)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc
    return qmef_validate_response_dict(ds)


@router.post("/v1/meta/ml-md-trainer-stub-fit")
def ml_md_trainer_stub_fit(body: QMEFTrainerStubFitBody) -> dict[str, object]:
    try:
        ds = validate_qmef_dict(body.qmef)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc
    return trainer_stub_fit_response_dict(ds, dict(body.hyperparams or {}))

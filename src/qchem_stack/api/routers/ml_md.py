from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import ValidationError

from qchem_stack.api.contract import with_api_contract
from qchem_stack.api.middleware import ML_MD_POST_LIMIT, rate_limit
from qchem_stack.api.models import QMEFTrainerStubFitBody, QMEFValidateBody
from qchem_stack.md_bridge.http_surface import (
    ml_md_bridge_surface_v1,
    qmef_validate_response_dict,
    trainer_stub_fit_response_dict,
    validate_qmef_dict,
)

router = APIRouter(tags=["ml_md"])


@router.get("/v1/meta/ml-md-bridge")
def ml_md_bridge_meta() -> dict[str, object]:
    return with_api_contract(ml_md_bridge_surface_v1())


@router.post("/v1/meta/qmef-validate")
@rate_limit(ML_MD_POST_LIMIT)
def qmef_validate(request: Request, body: Annotated[QMEFValidateBody, Body()]) -> dict[str, object]:
    try:
        ds = validate_qmef_dict(body.qmef)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc
    return with_api_contract(qmef_validate_response_dict(ds))


@router.post("/v1/meta/ml-md-trainer-stub-fit")
@rate_limit(ML_MD_POST_LIMIT)
def ml_md_trainer_stub_fit(
    request: Request, body: Annotated[QMEFTrainerStubFitBody, Body()]
) -> dict[str, object]:
    try:
        ds = validate_qmef_dict(body.qmef)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors(include_url=False)) from exc
    return with_api_contract(trainer_stub_fit_response_dict(ds, dict(body.hyperparams or {})))

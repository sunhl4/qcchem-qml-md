from __future__ import annotations

import pytest

from qchem_stack.contracts import (
    JOB_TIMELINE_V1,
    RDM_CORRECTION_REPORT_V1,
    assert_payload_schema,
    schema_field,
)
from qchem_stack.integrations.rdm_corrections_types import rdm_correction_report_v1


def test_schema_field_roundtrip() -> None:
    payload = schema_field(JOB_TIMELINE_V1) | {"events": []}
    assert_payload_schema(payload, JOB_TIMELINE_V1)


def test_assert_payload_schema_raises() -> None:
    with pytest.raises(ValueError, match="expected schema="):
        assert_payload_schema({"schema": "other_v1"}, JOB_TIMELINE_V1)


def test_rdm_correction_report_builder_schema() -> None:
    rep = rdm_correction_report_v1(method="stub_nevpt2", status="stub")
    assert_payload_schema(rep, RDM_CORRECTION_REPORT_V1)

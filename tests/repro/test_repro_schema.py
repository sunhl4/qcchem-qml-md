from __future__ import annotations

import pytest

from qchem_stack.contracts.schema_ids import PARITY_EXPORT_SCHEMA_VERSION_V3
from qchem_stack.protocols.product_contract import PARITY_EXPORT_V3_STABLE_KEYS
from qchem_stack.repro.schema import (
    PIPELINE_PROFILE_SCHEMA_V1,
    PRE_QUANTUM_HANDOFF_SCHEMA_V1,
    WORKFLOW_PREVIEW_REPRO_SCHEMA_V1,
    assert_parity_export_keys_stable,
    assert_parity_export_schema_version,
)


def test_assert_parity_export_keys_stable_passes() -> None:
    payload = {k: f"v_{k}" for k in PARITY_EXPORT_V3_STABLE_KEYS}
    assert_parity_export_keys_stable(payload)


def test_assert_parity_export_keys_stable_raises() -> None:
    with pytest.raises(KeyError, match="missing stable keys"):
        assert_parity_export_keys_stable({})


def test_assert_parity_export_keys_stable_reports_partial_missing() -> None:
    keys = list(PARITY_EXPORT_V3_STABLE_KEYS)
    payload = {k: f"v_{k}" for k in keys[:-1]}
    with pytest.raises(KeyError, match=keys[-1]) as exc:
        assert_parity_export_keys_stable(payload)
    assert "missing stable keys" in str(exc.value)


def test_assert_parity_export_schema_version() -> None:
    payload = {k: f"v_{k}" for k in PARITY_EXPORT_V3_STABLE_KEYS}
    payload["parity_export_schema_version"] = PARITY_EXPORT_SCHEMA_VERSION_V3
    assert_parity_export_schema_version(payload)
    with pytest.raises(ValueError, match="parity_export_schema_version"):
        assert_parity_export_schema_version({"parity_export_schema_version": 2})


def test_assert_parity_export_schema_version_missing_key() -> None:
    with pytest.raises(ValueError, match="parity_export_schema_version"):
        assert_parity_export_schema_version({})


def test_schema_id_aliases_are_nonempty_strings() -> None:
    assert isinstance(PRE_QUANTUM_HANDOFF_SCHEMA_V1, str) and PRE_QUANTUM_HANDOFF_SCHEMA_V1
    assert isinstance(PIPELINE_PROFILE_SCHEMA_V1, str) and PIPELINE_PROFILE_SCHEMA_V1
    assert isinstance(WORKFLOW_PREVIEW_REPRO_SCHEMA_V1, str) and WORKFLOW_PREVIEW_REPRO_SCHEMA_V1

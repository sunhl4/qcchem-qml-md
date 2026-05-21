from __future__ import annotations

import pytest

from qchem_stack.contracts.schema_ids import PARITY_EXPORT_SCHEMA_VERSION_V3
from qchem_stack.protocols.product_contract import PARITY_EXPORT_V3_STABLE_KEYS
from qchem_stack.repro.schema import (
    assert_parity_export_keys_stable,
    assert_parity_export_schema_version,
)


def test_assert_parity_export_keys_stable_passes() -> None:
    payload = {k: f"v_{k}" for k in PARITY_EXPORT_V3_STABLE_KEYS}
    assert_parity_export_keys_stable(payload)


def test_assert_parity_export_keys_stable_raises() -> None:
    with pytest.raises(KeyError, match="missing stable keys"):
        assert_parity_export_keys_stable({})


def test_assert_parity_export_schema_version() -> None:
    payload = {k: f"v_{k}" for k in PARITY_EXPORT_V3_STABLE_KEYS}
    payload["parity_export_schema_version"] = PARITY_EXPORT_SCHEMA_VERSION_V3
    assert_parity_export_schema_version(payload)
    with pytest.raises(ValueError, match="parity_export_schema_version"):
        assert_parity_export_schema_version({"parity_export_schema_version": 2})

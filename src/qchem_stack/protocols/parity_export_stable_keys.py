"""Parity export stable-key validation (re-export from parity_export_types)."""

from __future__ import annotations

from typing import Any

from qchem_stack.protocols.parity_export_types import assert_stable_keys_present


def _assert_parity_export_v3_stable_keys(table: dict[str, Any]) -> None:
    assert_stable_keys_present(table)

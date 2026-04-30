"""Helpers for job store meta filtering."""

from __future__ import annotations

from qchem_stack.jobs.store import _meta_experiment_id_from_raw, _meta_top_str


def test_meta_top_str() -> None:
    assert _meta_top_str('{"api_workspace_label": "p"}', "api_workspace_label") == "p"
    assert _meta_top_str(None, "x") is None


def test_meta_experiment_id_from_raw() -> None:
    assert _meta_experiment_id_from_raw(None) is None
    assert _meta_experiment_id_from_raw("") is None
    assert _meta_experiment_id_from_raw("not json") is None
    assert _meta_experiment_id_from_raw('{"experiment_id": "z"}') == "z"
    assert _meta_experiment_id_from_raw('{"other": 1}') is None

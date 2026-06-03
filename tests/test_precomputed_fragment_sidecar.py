"""Precomputed fragment / MI-FNO sidecar plugin hook tests (P2-R03)."""

from __future__ import annotations

from qchem_stack.integrations.precomputed_fragment import (
    load_precomputed_fragment_sidecar,
    merge_precomputed_fragment_into_workflow,
)
from tests.helpers.paths import fixtures_path


def test_load_precomputed_fragment_sidecar_sets_schema() -> None:
    sidecar = load_precomputed_fragment_sidecar(
        fixtures_path("precomputed_fragment_h4_sidecar.json")
    )
    assert sidecar["schema"] == "precomputed_fragment_input_v1"
    assert sidecar["status"] == "input_only"
    assert len(sidecar["fragments"]) == 2


def test_merge_precomputed_fragment_into_workflow_attaches_metadata() -> None:
    sidecar = load_precomputed_fragment_sidecar(
        fixtures_path("precomputed_fragment_h4_sidecar.json")
    )
    wf = merge_precomputed_fragment_into_workflow({"mode": "schmidt"}, sidecar)
    assert wf["mode"] == "schmidt"
    assert wf["mi_fno_plugin_status"] == "input_only"
    assert wf["precomputed_fragment_sidecar_v1"]["system"] == "h4_linear_chain_stub"

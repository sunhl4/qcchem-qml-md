"""L1 phase J (序 26): ``inquanto_gap_categories`` row shape regression."""

from __future__ import annotations

import pytest

from qchem_stack.protocols.inquanto_contract import inquanto_gap_categories


@pytest.mark.parametrize(
    "row_id",
    [
        "cloud_nexus",
        "http_submit_poll_workspace",
        "qermit_graph",
        "composable_computable",
        "evaluate_support_set",
        "compiler_pass_bundle",
        "ucc_chem_ansatz",
        "dmet_scf_loop",
        "tensornet",
        "integrations_closure_layer",
        "drivers_cosmo_pbc",
        "qpu_shot_histogram",
    ],
)
def test_gap_category_row_exists_with_core_fields(row_id: str) -> None:
    rows = inquanto_gap_categories()
    row = next(r for r in rows if r.get("id") == row_id)
    for key in ("id", "parity_matrix_anchor", "inquanto_surface", "qchem_stack", "status"):
        assert key in row and row[key]


def test_qermit_gap_has_execution_model_nested() -> None:
    rows = inquanto_gap_categories()
    qg = next(r for r in rows if r.get("id") == "qermit_graph")
    mm = qg.get("mitigation_execution_model")
    assert isinstance(mm, dict)
    assert mm.get("schema") == "mitigation_execution_model_v1"

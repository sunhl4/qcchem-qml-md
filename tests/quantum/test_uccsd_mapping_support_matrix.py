from __future__ import annotations

from qchem_stack.quantum.algorithms.uccsd_vqe import uccsd_mapping_support_matrix_v1


def test_uccsd_mapping_support_matrix_v1_schema_and_rows() -> None:
    m = uccsd_mapping_support_matrix_v1()
    assert m.get("schema") == "uccsd_mapping_support_matrix_v1"
    rows = m.get("rows")
    assert isinstance(rows, list) and rows
    by_map = {str(r.get("fermion_qubit_mapping")): r for r in rows if isinstance(r, dict)}
    assert by_map["jordan_wigner"]["support_status"] == "supported"
    assert by_map["bravyi_kitaev"]["support_status"] == "supported"
    assert by_map["symmetry_conserving_bravyi_kitaev"]["support_status"] == "not_supported"

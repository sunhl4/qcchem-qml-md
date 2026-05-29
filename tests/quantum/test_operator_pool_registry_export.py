from __future__ import annotations

from qchem_stack.quantum.operator_pool_registry import operator_pool_registry_export_v1


def test_operator_pool_registry_export_schema() -> None:
    blk = operator_pool_registry_export_v1()
    assert blk.get("schema") == "operator_pool_registry_export_v1"
    pools = blk.get("pools")
    assert isinstance(pools, dict) and pools
    ferm = pools.get("fermionic_uccsd")
    assert isinstance(ferm, dict) and ferm.get("summary")
    caps = ferm.get("capabilities")
    assert isinstance(caps, dict)
    assert blk.get("pool_id_aliases") == {
        "qubit_excitation": "iqeb_qubit_excitation",
        "uccsd_jw": "fermionic_uccsd",
        "uccsd_singles": "fermionic_uccsd_singles",
        "uccsd_doubles_only": "fermionic_uccsd_doubles_only",
        "uccsd_bravyi_kitaev": "fermionic_uccsd_bravyi_kitaev",
        "uccsd_bk": "fermionic_uccsd_bravyi_kitaev",
        "uccsd_bk_singles": "fermionic_uccsd_singles_bravyi_kitaev",
        "uccsd_bk_doubles_only": "fermionic_uccsd_doubles_bravyi_kitaev_only",
        "uccsd_bk_singles_then_doubles": "fermionic_uccsd_singles_then_doubles_bk_concat",
    }
    canon = blk.get("canonical_operator_pool_ids")
    assert isinstance(canon, list) and "fermionic_uccsd_bravyi_kitaev" in canon
    reg = blk.get("registered_ids")
    assert isinstance(reg, list) and "uccsd_bravyi_kitaev" in reg and "uccsd_bk" in reg

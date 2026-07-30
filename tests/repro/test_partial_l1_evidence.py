"""L1 evidence smoke tests for partial→yes convergence (Phase M P2-E03)."""

from __future__ import annotations

import pytest

from qchem_stack.protocols.product_contract import product_gap_categories
from tests.helpers.paths import configs_path


def test_product_gap_categories_have_anchors() -> None:
    from qchem_stack.protocols.product_contract import validate_product_gap_categories

    gaps = product_gap_categories()
    assert gaps
    assert not validate_product_gap_categories()
    for row in gaps:
        assert row.get("id")
        assert row.get("release_anchor")
        assert row.get("status")


def test_product_capability_sla_v1_normalizes_statuses() -> None:
    from qchem_stack.contracts.schema_ids import PRODUCT_CAPABILITY_SLA_V1
    from qchem_stack.protocols.product_contract import product_capability_sla_v1

    allowed = {"available", "partial", "stub_only", "n/a", "local_runtime_only"}
    payload = product_capability_sla_v1()
    assert payload["schema"] == PRODUCT_CAPABILITY_SLA_V1
    gaps = product_gap_categories()
    assert set(payload["by_id"]) == {row["id"] for row in gaps}
    assert len(payload["rows"]) == len(gaps)
    for row in payload["rows"]:
        assert row["sla"] in allowed
    assert payload["by_id"]["mitigation_batch_scheduler"] == "partial"
    assert payload["by_id"]["tensor_network_engine"] == "stub_only"
    assert payload["by_id"]["managed_cloud_runtime"] == "local_runtime_only"
    assert payload["by_id"]["uccsd_scbk_trotter_circuit"] == "n/a"


def test_product_gap_evidence_paths_exist_on_disk() -> None:
    from pathlib import Path

    from qchem_stack.protocols.product_contract import validate_product_gap_categories

    assert not validate_product_gap_categories()
    repo_root = Path(__file__).resolve().parents[2]
    for row in product_gap_categories():
        for path in row.get("evidence") or []:
            assert (repo_root / path).is_file(), f"missing evidence: {path}"


def test_dmet_self_consistency_l1_yaml_exists() -> None:
    p = configs_path("example_h4_dmet_self_consistent.yaml")
    assert p.is_file()
    assert configs_path("example_h2_dimer_dmet_self_consistent.yaml").is_file()
    assert configs_path("example_h2_uniform_multifragment_toy.yaml").is_file()


def test_adapt_iqeb_operator_pool_l1_yamls_exist() -> None:
    for name in (
        "example_h2_adapt_staggered_pool.yaml",
        "example_h2_adapt_bk_pool.yaml",
        "example_h2_adapt_generalized_doubles_pool.yaml",
        "example_h2_iqeb_bk_singles_pool.yaml",
    ):
        assert configs_path(name).is_file()


def test_operator_pool_ids_resolve_for_l1_yamls() -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.quantum.operator_pool_registry import is_registered_operator_pool_id

    cases = (
        ("example_h2_adapt_bk_pool.yaml", "fermionic_uccsd_bravyi_kitaev"),
        ("example_h2_adapt_generalized_doubles_pool.yaml", "fermionic_generalized_doubles"),
        ("example_h2_iqeb_bk_singles_pool.yaml", "fermionic_uccsd_singles_bravyi_kitaev"),
    )
    for cfg_name, pool_id in cases:
        cfg = load_experiment_config(configs_path(cfg_name))
        resolved = (
            cfg.quantum.adapt.pool_id
            if cfg.quantum.algorithm == "adapt"
            else cfg.quantum.iqeb.pool_id
        )
        assert resolved == pool_id
        assert is_registered_operator_pool_id(str(resolved))


def test_workflow_preview_repro_alignment_module_importable() -> None:
    pytest.importorskip("fastapi")
    from qchem_stack.protocols.workflow_preview import workflow_preview_payload

    assert callable(workflow_preview_payload)


def test_vqd_deflation_yaml_in_parity_sample() -> None:
    p = configs_path("example_h2_vqd_uccsd.yaml")
    assert p.is_file()
    p2 = configs_path("example_h2_vqd_deflation_circuit.yaml")
    assert p2.is_file()


def test_vqd_deflation_circuit_export_config_has_overlap_mode() -> None:
    from qchem_stack.config import load_experiment_config

    cfg = load_experiment_config(configs_path("example_h2_vqd_deflation_circuit.yaml"))
    assert cfg.quantum.excited.vqd.overlap_mode == "deflation_circuit"


def test_scbk_hea_mapping_yaml_exists() -> None:
    assert configs_path("example_h2_scbk_hea.yaml").is_file()

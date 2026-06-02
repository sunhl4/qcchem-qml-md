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


def test_dmet_self_consistency_l1_yaml_exists() -> None:
    p = configs_path("example_h4_dmet_self_consistent.yaml")
    assert p.is_file()


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

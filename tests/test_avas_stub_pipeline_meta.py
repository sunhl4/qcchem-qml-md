"""AVAS stub strategy records honesty metadata on ``hamiltonian_meta.pyscf_driver``."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_avas_stub_yaml_sets_driver_meta_flags() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_h2_avas_stub.yaml"
    cfg = load_experiment_config(p)
    assert cfg.active_space.strategy == "avas_stub"
    out = run_pipeline_sync(cfg, cfg_path=p)
    pd = (out.get("hamiltonian_meta") or {}).get("pyscf_driver") or {}
    assert pd.get("avas_partial_stub") is True
    assert pd.get("avas_atomic_projection_executed") is False
    assert (
        pd.get("avas_stub_semantics")
        == "cas_ncas_nelecas_equivalent_no_avas_threshold_projection_v1"
    )
    assert pd.get("avas_ao_labels_logging_only") is True
    assert pd.get("active_space_strategy") == "avas_stub"
    assert pd.get("avas_ao_labels_requested") == ["H 1s"]

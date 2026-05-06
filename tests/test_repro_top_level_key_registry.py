"""``repro`` root keys must stay registered (P1 Methods / CI)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import collect_repro_metadata
from qchem_stack.protocols.inquanto_contract import REPRO_DOCUMENTED_KEYS


def test_collect_repro_metadata_root_keys_whitelisted() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    repro = collect_repro_metadata(cfg, cfg_path=cfg_path)
    unknown = set(repro.keys()) - REPRO_DOCUMENTED_KEYS
    assert not unknown, f"Add keys to REPRO_DOCUMENTED_KEYS or fix repro: {sorted(unknown)}"


@pytest.mark.skipif(
    not Path(__file__).resolve().parents[1].joinpath("configs", "example_h2.yaml").is_file(),
    reason="sample config",
)
def test_full_pipeline_repro_root_keys_whitelisted() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    repro = out.get("repro")
    assert isinstance(repro, dict)
    unknown = set(repro.keys()) - REPRO_DOCUMENTED_KEYS
    assert not unknown, f"Unexpected repro keys: {sorted(unknown)}"

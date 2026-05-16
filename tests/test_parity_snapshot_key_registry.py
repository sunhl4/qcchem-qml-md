"""Parity snapshot keys must stay registered for L1 CI (see ``PARITY_SNAPSHOT_DOCUMENTED_KEYS``)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.protocols.inquanto_contract import (
    PARITY_SNAPSHOT_DOCUMENTED_KEYS,
)
from qchem_stack.orchestration.pipeline import _repro_quantum_snapshot, collect_repro_metadata


def test_collect_repro_metadata_parity_keys_whitelisted() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    repro = collect_repro_metadata(cfg, cfg_path=cfg_path)
    snap = repro.get("parity_snapshot")
    assert isinstance(snap, dict)
    unknown = set(snap.keys()) - PARITY_SNAPSHOT_DOCUMENTED_KEYS
    assert not unknown, (
        f"Add keys to PARITY_SNAPSHOT_DOCUMENTED_KEYS or fix snapshot: {sorted(unknown)}"
    )


def test_repro_quantum_snapshot_minimal_config_whitelisted() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    snap = _repro_quantum_snapshot(cfg, None)
    unknown = set(snap.keys()) - PARITY_SNAPSHOT_DOCUMENTED_KEYS
    assert not unknown, f"Unexpected keys: {sorted(unknown)}"


@pytest.mark.skipif(
    not Path(__file__).resolve().parents[1].joinpath("configs", "example_h2.yaml").is_file(),
    reason="sample config",
)
def test_finalize_adds_tensornet_parity_keys_when_stub_runs() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("pyscf not installed")
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    cfg = cfg.model_copy(
        update={
            "quantum": cfg.quantum.model_copy(
                update={"tensornet_expectation_stub": True, "tensornet_contraction_engine": "stub"}
            )
        }
    )
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    snap = out.get("repro", {}).get("parity_snapshot")
    assert isinstance(snap, dict)
    assert "tensornet_engine_resolved" in snap
    assert "tensornet_fallback_reason" in snap
    assert snap["tensornet_engine_resolved"]
    assert snap["tensornet_fallback_reason"]

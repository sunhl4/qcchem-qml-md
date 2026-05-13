"""D44: gap closure bundle stable schema + minimal keys."""

from __future__ import annotations

from pathlib import Path

from qchem_stack.config import load_experiment_config
from qchem_stack.integrations.gap_closure_bundle import build_open_gap_closure_reference

_ROOT = Path(__file__).resolve().parents[1]


def test_open_gap_closure_reference_v1_shape() -> None:
    cfg = load_experiment_config(_ROOT / "configs" / "example_h2.yaml")
    blob = build_open_gap_closure_reference(cfg)
    assert blob["schema"] == "open_gap_closure_reference_v1"
    assert "ucc" in blob and "tket" in blob and "qermit" in blob
    assert blob["ucc"].get("policies_implemented")

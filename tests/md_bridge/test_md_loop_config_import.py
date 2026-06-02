"""Smoke: md_loop_config must import without NameError on DEFAULT_LEARNING_RATE."""

from __future__ import annotations

from qchem_stack.md_bridge.md_loop_config import MdValidationLoopConfig
from qchem_stack.quantum.algorithms.tolerances import DEFAULT_LEARNING_RATE


def test_md_validation_loop_config_default_learning_rate() -> None:
    cfg = MdValidationLoopConfig()
    assert cfg.learning_rate == DEFAULT_LEARNING_RATE


def test_md_loop_config_module_importable() -> None:
    import qchem_stack.md_bridge.md_loop_config as m

    assert m.MdValidationLoopConfig is not None

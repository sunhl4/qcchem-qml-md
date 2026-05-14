from __future__ import annotations

import runpy
from pathlib import Path


def test_sample_configs_include_vqd_uccsd_and_are_unique() -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "check_parity_export_sample.py"
    namespace = runpy.run_path(str(script))
    sample_configs = tuple(namespace["SAMPLE_CONFIGS_REL"])
    assert "configs/example_h2_vqd_uccsd.yaml" in sample_configs
    assert len(sample_configs) == len(set(sample_configs))

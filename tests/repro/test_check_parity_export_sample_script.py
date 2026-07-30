from __future__ import annotations

import runpy

from tests.helpers.paths import repo_root


def test_sample_configs_include_vqd_uccsd_and_are_unique() -> None:
    root = repo_root()
    script = root / "scripts" / "check_parity_export_sample.py"
    namespace = runpy.run_path(str(script))
    sample_configs = tuple(namespace["SAMPLE_CONFIGS_REL"])
    md_loop_configs = tuple(namespace["MD_LOOP_CONFIGS_REL"])
    assert "configs/example_h2_vqd_uccsd.yaml" in sample_configs
    assert len(sample_configs) == len(set(sample_configs))
    assert len(sample_configs) >= 96
    # MD-loop configs are auto-discovered from configs/*.yaml (see
    # scripts/check_parity_export_sample.py), so assert a floor + uniqueness
    # rather than an exact count that drifts when configs are added.
    assert len(md_loop_configs) >= 11
    assert len(md_loop_configs) == len(set(md_loop_configs))

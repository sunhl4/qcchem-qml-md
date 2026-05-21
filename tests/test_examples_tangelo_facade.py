"""Packaged YAML loaders exposed for notebook ergonomics."""

from __future__ import annotations

from examples.tangelo_facade_demo import (
    load_packaged_example,
    packaged_config_path,
    packaged_example_names,
)


def test_packaged_paths_exist_and_load() -> None:
    for name in packaged_example_names():
        p = packaged_config_path(name)
        assert p.is_file(), p
    cfg = load_packaged_example("h2_pec_stub")
    assert cfg.experiment_id == "h2_sto3g_pec_stub_demo"
    assert cfg.mitigation.stubs.pec_literature is True

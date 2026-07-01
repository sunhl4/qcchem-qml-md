"""L1 pipeline smoke: ADAPT operator pools resolve through run_summary."""

from __future__ import annotations

import pytest

pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.helpers.paths import configs_path


@pytest.mark.parametrize(
    ("config_name", "expected_pool_id"),
    [
        ("example_h2_adapt_bk_pool.yaml", "fermionic_uccsd_bravyi_kitaev"),
        ("example_h2_adapt_generalized_doubles_pool.yaml", "fermionic_generalized_doubles"),
    ],
)
def test_adapt_pool_id_yaml_in_run_summary(
    tmp_path, config_name: str, expected_pool_id: str
) -> None:
    src = configs_path(config_name)
    assert src.is_file()
    text = src.read_text(encoding="utf-8")
    text = text.replace("max_iter: 3", "max_iter: 2", 1)
    cfg_path = tmp_path / config_name
    cfg_path.write_text(text, encoding="utf-8")
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    rs = out["repro"]["run_summary"]
    assert rs.get("adapt_pool_id_yaml") == expected_pool_id

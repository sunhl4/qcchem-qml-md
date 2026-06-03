"""Golden key-set regression for ``run_pipeline_sync`` (no numeric asserts)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from tests.helpers.h2_yaml import write_h2_pipeline_yaml
from tests.helpers.paths import repo_root

_FIXTURE = repo_root() / "tests" / "fixtures" / "pipeline_h2_sync_core_keys.json"


def _load_fixture() -> dict:
    return json.loads(_FIXTURE.read_text(encoding="utf-8"))


def test_pipeline_sync_core_keys_superset_of_fixture(tmp_path: Path) -> None:
    cfg_path = write_h2_pipeline_yaml(
        tmp_path / "h2_keys.yaml",
        experiment_id="keys_fixture",
        backend={"shots_per_circuit": 512},
        quantum={"vqe": {"maxiter": 120}, "pauli": {"use_protocol": True}},
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    spec = _load_fixture()
    missing_top = sorted(set(spec["top_level"]) - set(out.keys()))
    assert not missing_top, f"missing top-level keys: {missing_top}"
    repro = out.get("repro")
    assert isinstance(repro, dict)
    missing_repro = sorted(set(spec["repro"]) - set(repro.keys()))
    assert not missing_repro, f"missing repro keys: {missing_repro}"

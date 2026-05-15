"""``repro`` root keys must stay registered (P1 Methods / CI)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.internal_reports.competitor.inquanto_contract import REPRO_DOCUMENTED_KEYS
from qchem_stack.orchestration.pipeline import collect_repro_metadata


def test_collect_repro_metadata_root_keys_whitelisted() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2.yaml"
    cfg = load_experiment_config(cfg_path)
    repro = collect_repro_metadata(cfg, cfg_path=cfg_path)
    unknown = set(repro.keys()) - REPRO_DOCUMENTED_KEYS
    assert not unknown, f"Add keys to REPRO_DOCUMENTED_KEYS or fix repro: {sorted(unknown)}"


@pytest.mark.skipif(
    not Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("configs", "example_h2_echo_variational_plugin.yaml")
    .is_file(),
    reason="echo plugin config",
)
def test_collect_repro_metadata_includes_variational_execution_slice_when_factory_yaml() -> None:
    cfg_path = (
        Path(__file__).resolve().parents[1] / "configs" / "example_h2_echo_variational_plugin.yaml"
    )
    cfg = load_experiment_config(cfg_path)
    repro = collect_repro_metadata(cfg, cfg_path=cfg_path)
    unknown = set(repro.keys()) - REPRO_DOCUMENTED_KEYS
    assert not unknown, sorted(unknown)
    wv = repro.get("workflow_preview_variational_execution_v1")
    assert isinstance(wv, dict)
    assert wv.get("schema") == "variational_yaml_plugin_dispatch_v1"
    assert wv.get("algorithm_factory")
    nested = (repro.get("workflow_preview_v1") or {}).get("variational_execution")
    assert nested == wv


@pytest.mark.skipif(
    not Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("configs", "example_h2_vqs_track.yaml")
    .is_file(),
    reason="VQS track sample config missing",
)
def test_collect_repro_metadata_includes_vqs_workflow_slice_when_track_yaml() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2_vqs_track.yaml"
    cfg = load_experiment_config(cfg_path)
    repro = collect_repro_metadata(cfg, cfg_path=cfg_path)
    unknown = set(repro.keys()) - REPRO_DOCUMENTED_KEYS
    assert not unknown, sorted(unknown)
    wvq = repro.get("workflow_preview_vqs_track_v1")
    assert isinstance(wvq, dict) and wvq.get("schema") == "workflow_preview_vqs_track_v1"


@pytest.mark.skipif(
    not Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("configs", "qpe_dual_track_demo.yaml")
    .is_file(),
    reason="QPE dual-track sample config missing",
)
def test_collect_repro_metadata_includes_qpe_workflow_slice_when_track_yaml() -> None:
    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "qpe_dual_track_demo.yaml"
    cfg = load_experiment_config(cfg_path)
    repro = collect_repro_metadata(cfg, cfg_path=cfg_path)
    unknown = set(repro.keys()) - REPRO_DOCUMENTED_KEYS
    assert not unknown, sorted(unknown)
    wq = repro.get("workflow_preview_qpe_track_v1")
    assert isinstance(wq, dict) and wq.get("schema") == "workflow_preview_qpe_track_v1"


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


@pytest.mark.skipif(
    not Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("configs", "example_h2_vqs_track.yaml")
    .is_file(),
    reason="VQS track sample config missing",
)
def test_full_pipeline_vqs_yaml_repro_root_keys_whitelisted() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "example_h2_vqs_track.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    repro = out.get("repro")
    assert isinstance(repro, dict)
    unknown = set(repro.keys()) - REPRO_DOCUMENTED_KEYS
    assert not unknown, f"Unexpected repro keys: {sorted(unknown)}"
    assert isinstance(repro.get("workflow_preview_vqs_track_v1"), dict)


@pytest.mark.skipif(
    not Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("configs", "qpe_dual_track_demo.yaml")
    .is_file(),
    reason="QPE dual-track sample config missing",
)
def test_full_pipeline_qpe_dual_track_repro_root_keys_whitelisted() -> None:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = Path(__file__).resolve().parents[1] / "configs" / "qpe_dual_track_demo.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    repro = out.get("repro")
    assert isinstance(repro, dict)
    unknown = set(repro.keys()) - REPRO_DOCUMENTED_KEYS
    assert not unknown, f"Unexpected repro keys: {sorted(unknown)}"
    assert isinstance(repro.get("workflow_preview_qpe_track_v1"), dict)

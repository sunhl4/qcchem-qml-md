"""Pipeline → repro QMEF attachment (``md_ml_export``): pauli energy + trajectory."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.l1_md_ml


@pytest.fixture
def _require_pyscf():
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")


def test_pipeline_attaches_qmef_ml_attachment_v1_single_geometry(_require_pyscf) -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_md_ml_qmef_attach.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    repro = out["repro"]
    block = repro.get("qmef_ml_attachment_v1")
    assert isinstance(block, dict)
    assert block.get("schema") == "qmef_ml_attachment_v1"
    assert isinstance(block.get("frame_meta"), list) and len(block["frame_meta"]) == 1
    ds = block.get("dataset") or {}
    assert ds.get("frames") and len(ds["frames"]) == 1
    fr0 = ds["frames"][0]
    assert fr0.get("atomic_numbers") == [1, 1]
    assert fr0.get("energy_hartree") == pytest.approx(float(out["energy_after_variational"]))
    forces = fr0.get("forces_hartree_bohr") or []
    assert len(forces) == 2 and len(forces[0]) == 3


def test_energy_reference_pauli_protocol(_require_pyscf) -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_md_ml_pauli_energy.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    block = out["repro"]["qmef_ml_attachment_v1"]
    fr0 = block["dataset"]["frames"][0]
    assert fr0["energy_hartree"] == pytest.approx(float(out["energy_pauli_protocol"]))


def test_trajectory_hf_scf_appends_frames(_require_pyscf) -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_md_ml_trajectory_hf.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    block = out["repro"]["qmef_ml_attachment_v1"]
    ds = block["dataset"]
    assert len(ds["frames"]) == 3
    assert len(block["frame_meta"]) == 3
    assert block["frame_meta"][1]["energy_theory"] == "hf_scf_only"
    assert ds["frames"][1]["positions_bohr"][1][2] == pytest.approx(1.6)


@pytest.mark.slow
def test_trajectory_full_pipeline_nested_energy(_require_pyscf) -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_md_ml_trajectory_full_pipeline.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    block = out["repro"]["qmef_ml_attachment_v1"]
    assert block["frame_meta"][1]["energy_theory"] == "nested_full_pipeline"
    assert len(block["dataset"]["frames"]) == 2


def test_pipeline_respects_attach_flag_off(_require_pyscf) -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_md_ml_qmef_attach.yaml"
    cfg = load_experiment_config(cfg_path)
    cfg.md_ml_export.attach_single_frame_to_repro = False
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert "qmef_ml_attachment_v1" not in (out.get("repro") or {})


def test_md_ml_extra_coordinates_validation() -> None:
    from pydantic import ValidationError

    from qchem_stack.config import ExperimentConfig, load_experiment_config

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_md_ml_qmef_attach.yaml")
    payload = cfg.model_dump(mode="json")
    payload["md_ml_export"]["extra_coordinates_bohr"] = [[[0.0, 0.0, 0.0]]]
    with pytest.raises(ValidationError):
        ExperimentConfig.model_validate(payload)


def test_pauli_energy_yaml_requires_use_pauli() -> None:
    from pydantic import ValidationError

    from qchem_stack.config import ExperimentConfig, load_experiment_config

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_md_ml_qmef_attach.yaml")
    payload = cfg.model_dump(mode="json")
    payload["md_ml_export"]["attach_single_frame_to_repro"] = True
    payload["md_ml_export"]["energy_reference"] = "pauli_protocol"
    payload["quantum"]["use_pauli_protocol"] = False
    with pytest.raises(ValidationError):
        ExperimentConfig.model_validate(payload)

"""UQC mock backend + MD/ML (QMEF + online learning loop) — no real hardware."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = [pytest.mark.l1_md_ml, pytest.mark.uqc_mock]

ROOT = Path(__file__).resolve().parents[1]
EXP_YAML = ROOT / "configs" / "example_h2_uqc_mock_md_ml.yaml"
LOOP_YAML = ROOT / "configs" / "example_h2_uqc_mock_qmlff_loop.yaml"


@pytest.fixture
def _require_pyscf():
    try:
        import pyscf  # noqa: F401
    except ImportError:
        pytest.skip("PySCF not installed")


def test_uqc_mock_backend_registered_and_mock_energy() -> None:
    from qchem_stack.backends import executor_from_spec, registered_backend_provider_ids
    from qchem_stack.config import backend_spec_from_config, load_experiment_config

    assert "uqc" in registered_backend_provider_ids()
    cfg = load_experiment_config(EXP_YAML)
    assert cfg.backend.provider == "uqc"
    assert cfg.backend.uqc_mode == "mock"

    spec = backend_spec_from_config(cfg)
    ex = executor_from_spec(spec)
    assert type(ex).__name__ == "UQCCloudHeaExecutor"

    import numpy as np
    from openfermion.ops import QubitOperator

    h = QubitOperator("Z0 Z1", 1.0)
    e = ex.expectation_hea(h, 2, np.zeros(4), 1)
    assert pytest.approx(1.0) == e


def test_pipeline_uqc_mock_attaches_qmef_for_md_ml(_require_pyscf) -> None:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg = load_experiment_config(EXP_YAML)
    out = run_pipeline_sync(cfg, cfg_path=EXP_YAML)
    assert cfg.backend.provider == "uqc"
    assert out.get("energy_after_variational") is not None

    block = out["repro"]["qmef_ml_attachment_v1"]
    assert block.get("schema") == "qmef_ml_attachment_v1"
    fr0 = block["dataset"]["frames"][0]
    assert fr0["energy_hartree"] == pytest.approx(float(out["energy_after_variational"]))


@pytest.mark.slow
def test_md_validation_loop_one_round_uqc_mock_labeling(_require_pyscf) -> None:
    pytest.importorskip("qmlff")
    pytest.importorskip("jax_md")

    from qchem_stack.md_bridge import MdValidationLoopConfig, run_md_validation_loop

    loop_cfg = MdValidationLoopConfig.from_yaml(LOOP_YAML)
    assert loop_cfg.label_energy_reference == "variational"

    summary = run_md_validation_loop(
        EXP_YAML,
        config=loop_cfg,
        output_dir=ROOT / "results" / "uqc_mock_md_ml_test",
    )
    assert summary["rounds"]
    assert summary["rounds"][0]["n_md_frames_sampled"] >= 1
    assert summary["n_total_frames"] >= 1

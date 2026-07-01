"""Unit tests for md_loop_summary, active_learning, and qml_kernel stubs."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from qchem_stack.exceptions import MDBridgeError
from qchem_stack.md_bridge.active_learning import (
    ActiveLearningLoop,
    MockLabelingSpec,
    SurrogateEnergyModel,
    max_std_proxy,
    mock_labeling_result,
)
from qchem_stack.md_bridge.md_loop_config import (
    FrameValidationRecord,
    MdValidationLoopConfig,
    MdValidationRoundLog,
)
from qchem_stack.md_bridge.md_loop_summary import (
    build_md_validation_summary,
    json_default,
    round_log_to_jsonable,
    write_md_validation_summary,
    write_round_metrics,
)
from qchem_stack.md_bridge.qml_kernel import QuantumKernelEnergyModel


def test_quantum_kernel_energy_model_dataclass() -> None:
    model = QuantumKernelEnergyModel()
    assert "QMFrame" in model.note


def test_surrogate_energy_model_fit_predict_and_acquisition() -> None:
    x = np.array([[0.0], [1.0], [2.0]])
    y = np.array([-1.0, -1.1, -1.2])
    model = SurrogateEnergyModel()
    model.fit(x, y)
    preds = model.predict(x)
    assert preds.shape == (3,)

    loop = ActiveLearningLoop(pool_features=x, acquisition=max_std_proxy)
    idx = loop.next_index(model)
    assert idx in {0, 1, 2}

    with pytest.raises(MDBridgeError, match="call fit first"):
        SurrogateEnergyModel().predict(x)


def test_mock_labeling_result_builds_frames() -> None:
    res = mock_labeling_result(
        [1, 1],
        [[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]],
        [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.2]]],
        spec=MockLabelingSpec(base_energy_hartree=-1.0, per_extra_delta_hartree=0.05),
    )
    assert len(res.dataset.frames) == 2
    assert res.dataset.frames[1].energy_hartree == pytest.approx(-0.95)


def test_json_default_numpy_types() -> None:
    assert json_default(np.array([1.0, 2.0])) == [1.0, 2.0]
    assert json_default(np.float64(3.5)) == 3.5

    class _ScalarBox:
        def item(self) -> float:
            return 2.5

    assert json_default(_ScalarBox()) == 2.5
    with pytest.raises(TypeError):
        json_default(object())


def test_round_log_and_summary_writers(tmp_path: Path) -> None:
    frame = FrameValidationRecord(
        frame_index=0,
        time_ps=0.0,
        energy_qml_hartree=-1.0,
        energy_qchem_hartree=-1.01,
        delta_hartree=0.01,
        abs_delta_hartree=0.01,
        converged=True,
        theory_level="hf_scf",
        energy_reference_used="scf",
        delta_hartree_raw=0.01,
        abs_delta_hartree_raw=0.01,
    )
    log = MdValidationRoundLog(
        round_index=0,
        n_train_before=1,
        n_train_after=2,
        n_md_frames_sampled=1,
        max_abs_delta_hartree=0.01,
        mean_abs_delta_hartree=0.01,
        converged=True,
        training_metrics={"validation_energy_shift_hartree": 0.001},
        frames=[frame],
    )
    payload = round_log_to_jsonable(log)
    assert payload["round_index"] == 0
    assert len(payload["frames"]) == 1

    write_round_metrics(tmp_path, 0, log, {0: {"note": "debug"}})
    assert (tmp_path / "validation_round_0.json").is_file()

    cfg = MdValidationLoopConfig(energy_tolerance_hartree=0.05)
    summary = build_md_validation_summary(
        experiment_yaml=tmp_path / "exp.yaml",
        output_dir=tmp_path,
        config=cfg,
        n_total_frames=2,
        round_logs=[log],
        converged=True,
        species_list=["H", "H"],
    )
    assert summary["science_kpi_met"] is True
    assert summary["validation_energy_reference"] == "scf"
    write_md_validation_summary(tmp_path, summary)
    written = json.loads((tmp_path / "md_validation_summary.json").read_text(encoding="utf-8"))
    assert written["converged"] is True

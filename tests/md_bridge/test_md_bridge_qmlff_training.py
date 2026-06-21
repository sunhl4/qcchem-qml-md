"""QML-FF training multi-round smoke tests (stub path, no qmlff required)."""

from __future__ import annotations

import pytest

from qchem_stack.md_bridge.contracts import StubTorchMLIPTrainer
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame

pytestmark = pytest.mark.l1_md_ml


def _two_frame_dataset() -> QMEFDataset:
    frames = [
        QMFrame(
            atomic_numbers=[1, 1],
            positions_bohr=[[0, 0, 0], [0, 0, 1.2]],
            energy_hartree=-1.0,
            forces_hartree_bohr=[[0, 0, 0], [0, 0, 0]],
        ),
        QMFrame(
            atomic_numbers=[1, 1],
            positions_bohr=[[0, 0, 0], [0, 0, 1.6]],
            energy_hartree=-0.95,
            forces_hartree_bohr=[[0, 0, 0], [0, 0, 0.01]],
        ),
    ]
    return QMEFDataset(frames=frames, provenance_yaml="test: multi-round\n")


def test_stub_trainer_fit_two_rounds_stable_metrics() -> None:
    ds = _two_frame_dataset()
    trainer = StubTorchMLIPTrainer()
    art1 = trainer.fit(ds, {"lr": 1e-3, "epochs": 1})
    art2 = trainer.fit(ds, {"lr": 5e-4, "epochs": 2})
    assert art1.metrics["rmse_energy_mHa"] == 0.0
    assert art2.metrics["rmse_energy_mHa"] == 0.0

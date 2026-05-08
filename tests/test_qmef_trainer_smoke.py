"""Thin QMEF trainer smoke (StubTorchMLIPTrainer) — Day61–90 product-wrap anchor."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.l1_md_ml

from qchem_stack.md_bridge import QMEFDataset, QMFrame, StubTorchMLIPTrainer


def test_stub_torch_ml_ip_trainer_fit_and_export_smoke(tmp_path) -> None:
    fr = QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0, 0, 0], [0, 0, 1.4]],
        energy_hartree=-1.0,
        forces_hartree_bohr=[[0, 0, 0], [0, 0, 0]],
        method_tag="smoke",
    )
    ds = QMEFDataset(frames=[fr], provenance_yaml="qmef_trainer_smoke: true\n")
    tr = StubTorchMLIPTrainer()
    art = tr.fit(ds, {"lr": 1e-3})
    assert art.metrics["rmse_energy_mHa"] == 0.0
    tr.export_openmm(tmp_path / "omm.txt")
    tr.export_lammps(tmp_path / "lmp.txt")
    assert tmp_path.joinpath("omm.txt").read_text(encoding="utf-8")
    assert tmp_path.joinpath("lmp.txt").read_text(encoding="utf-8")

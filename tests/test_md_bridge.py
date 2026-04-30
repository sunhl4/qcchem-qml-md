from __future__ import annotations

import pytest

pytestmark = pytest.mark.l1_md_ml

from qchem_stack.md_bridge import QMEFDataset, QMFrame, StubTorchMLIPTrainer
from qchem_stack.md_bridge.exporter import export_extended_xyz, write_hdf5_stub
from qchem_stack.md_bridge.hooks import write_mace_yaml_stub, write_nequip_yaml_stub


def test_md_export_roundtrip(tmp_path) -> None:
    fr = QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0, 0, 0], [0, 0, 1.4]],
        energy_hartree=-1.0,
        forces_hartree_bohr=[[0, 0, 0], [0, 0, 0]],
        method_tag="RHF",
    )
    ds = QMEFDataset(frames=[fr], provenance_yaml="test: true\n")
    xyz = tmp_path / "d.xyz"
    export_extended_xyz(ds, xyz)
    assert xyz.read_text(encoding="utf-8").startswith("2\n")
    npz = tmp_path / "d.npz"
    write_hdf5_stub(ds, npz)
    assert npz.with_suffix(".npz").exists()
    write_nequip_yaml_stub(tmp_path / "n.yaml", str(npz))
    write_mace_yaml_stub(tmp_path / "m.yaml", str(npz))
    tr = StubTorchMLIPTrainer()
    art = tr.fit(ds, {"lr": 1e-3})
    assert art.metrics["rmse_energy_mHa"] == 0.0
    tr.export_openmm(tmp_path / "omm.txt")
    tr.export_lammps(tmp_path / "lmp.txt")

from __future__ import annotations

import pytest

from tests.helpers.paths import configs_path

pytestmark = pytest.mark.l1_md_ml

from qchem_stack.md_bridge import QMEFDataset, QMFrame, StubTorchMLIPTrainer

_FREEZE_QMFRAME_FIELDS = frozenset(
    {
        "atomic_numbers",
        "positions_bohr",
        "energy_hartree",
        "forces_hartree_bohr",
        "charge",
        "multiplicity",
        "box",
        "method_tag",
        "active_space_hash",
        "protocol_hash",
        "repro_config_sha256_prefix",
        "backend_noise_tag",
    }
)
from qchem_stack.md_bridge.exporter import export_extended_xyz, write_hdf5_stub
from qchem_stack.md_bridge.hooks import write_mace_yaml_stub, write_nequip_yaml_stub


def test_qmframe_fields_cover_p2_repro_freeze_doc() -> None:
    """P2-W6: ``docs/工程记忆_Quantinuum对标与数据流技术文档.md`` §16 must stay aligned with ``QMFrame``."""
    names = frozenset(QMFrame.model_fields)
    missing = sorted(_FREEZE_QMFRAME_FIELDS - names)
    assert not missing, f"QMFrame missing documented fields: {missing}"


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


def test_qmef_frame_can_carry_pipeline_repro_config_sha256_prefix() -> None:
    """P2-W6: ``QMFrame.repro_config_sha256_prefix`` aligns with ``repro.config_sha256_prefix`` policy."""

    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import collect_repro_metadata

    p = configs_path("example_h2.yaml")
    if not p.is_file():
        pytest.skip("example_h2.yaml missing")
    cfg = load_experiment_config(p)
    repro = collect_repro_metadata(cfg, cfg_path=p)
    prefix = repro.get("config_sha256_prefix")
    assert isinstance(prefix, str) and len(prefix) == 16
    fr = QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0, 0, 0], [0, 0, 1.4]],
        energy_hartree=-1.0,
        forces_hartree_bohr=[],
        repro_config_sha256_prefix=prefix,
    )
    assert fr.repro_config_sha256_prefix == prefix

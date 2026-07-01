"""Fast unit tests for md_bridge exporter, contracts, hooks, and from_pipeline branches."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from qchem_stack.config import ExperimentConfig
from qchem_stack.contracts.schema_ids import QMEF_ML_ATTACHMENT_V1
from qchem_stack.md_bridge.contracts import StubTorchMLIPTrainer
from qchem_stack.md_bridge.exporter import export_extended_xyz, write_hdf5_stub
from qchem_stack.md_bridge.from_pipeline import (
    build_qmef_dataset_single_frame_repro_block,
    build_qmef_ml_attachment_from_context,
    build_qmef_ml_attachment_repro_block,
)
from qchem_stack.md_bridge.from_pipeline_types import QmefAttachmentContext
from qchem_stack.md_bridge.hooks import write_mace_yaml_stub, write_nequip_yaml_stub
from qchem_stack.md_bridge.qchem_labeler import merge_qmef_datasets
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame


def _sample_frame(energy: float = -1.0, tag: str = "test") -> QMFrame:
    return QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]],
        energy_hartree=energy,
        forces_hartree_bohr=[[0.0, 0.0, 0.1], [0.0, 0.0, -0.1]],
        charge=0,
        multiplicity=1,
        box=None,
        method_tag=tag,
        active_space_hash="h",
        protocol_hash="p",
        repro_config_sha256_prefix="abc",
        backend_noise_tag="statevector",
    )


def _sample_dataset() -> QMEFDataset:
    return QMEFDataset(frames=[_sample_frame()], provenance_yaml="test: true\n")


def _h2_cfg(*, theory_level: str = "hf_scf", extra_coords: list | None = None) -> ExperimentConfig:
    extra = extra_coords or [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.2]]]
    return ExperimentConfig.model_validate(
        {
            "schema_version": "2",
            "experiment_id": "e",
            "random_seed": 0,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0, 0, 0], [0, 0, 0.74]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "active_space": {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
            "md_ml_export": {
                "attach_single_frame_to_repro": True,
                "energy_reference": "variational",
                "trajectory": {
                    "extra_coordinates_bohr": extra,
                    "theory_level": theory_level,
                },
            },
        }
    )


def test_export_extended_xyz_and_npz_stub(tmp_path: Path) -> None:
    ds = _sample_dataset()
    xyz = tmp_path / "out.xyz"
    export_extended_xyz(ds, xyz)
    text = xyz.read_text(encoding="utf-8")
    assert "energy=" in text
    assert "H " in text

    npz_path = tmp_path / "data.h5"
    write_hdf5_stub(ds, npz_path)
    assert npz_path.with_suffix(".npz").is_file()


def test_hook_yaml_stubs(tmp_path: Path) -> None:
    nequip = tmp_path / "nequip.yaml"
    write_nequip_yaml_stub(nequip, "dataset.npz")
    assert "NequIP" in nequip.read_text(encoding="utf-8")

    mace = tmp_path / "mace.yaml"
    write_mace_yaml_stub(mace, "dataset.npz")
    assert mace.read_text(encoding="utf-8")


def test_stub_torch_mlip_trainer_exports(tmp_path: Path) -> None:
    trainer = StubTorchMLIPTrainer()
    ds = _sample_dataset()
    art = trainer.fit(ds, {"lr": 1e-3})
    assert art.path == "stub_model.pt"
    assert art.meta["n_frames"] == 1

    openmm = tmp_path / "model.xml"
    trainer.export_openmm(str(openmm))
    assert "OpenMM" in openmm.read_text(encoding="utf-8")

    lammps = tmp_path / "pair.in"
    trainer.export_lammps(str(lammps))
    assert "LAMMPS" in lammps.read_text(encoding="utf-8")

    scores = trainer.score(ds)
    assert scores["kendall_tau"] == 1.0


def test_merge_qmef_datasets_concatenates_frames() -> None:
    a = _sample_dataset()
    b = QMEFDataset(
        frames=[
            _sample_frame(
                energy=-1.5,
                tag="b",
            ).model_copy(update={"positions_bohr": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.2]]})
        ],
        provenance_yaml="b: true\n",
    )
    merged = merge_qmef_datasets(a, b)
    assert len(merged.frames) == 2
    assert merged.provenance_yaml


def test_build_qmef_attachment_hf_scf_extra(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference

    cfg = _h2_cfg(theory_level="hf_scf")
    out = {"scf_energy": -1.1, "energy_after_variational": -1.2, "repro": {}}
    reference = MagicMock(spec=ClassicalMeanFieldReference)
    mock_rhf = MagicMock()
    mock_rhf.e_tot = -1.05
    mock_rhf.mol = MagicMock()
    mock_rhf.mol.atom = [(1, (0, 0, 0)), (1, (0, 0, 0.74))]

    primary = _sample_frame(energy=-1.2)
    extra = _sample_frame(energy=-1.05, tag="hf_scf")

    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.as_pyscf_rhf",
        lambda _ref: mock_rhf,
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.primary_qmframe",
        lambda _cfg, _out, _rhf: primary,
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.rhf_at_coordinates",
        lambda _cfg, _coords: mock_rhf,
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline_extract.qmframe_from_rhf",
        lambda *_a, **_k: extra,
    )

    block = build_qmef_ml_attachment_repro_block(cfg, out, reference)
    assert block["schema"] == QMEF_ML_ATTACHMENT_V1
    assert len(block["dataset"]["frames"]) == 2
    assert block["frame_meta"][1]["energy_theory"] == "hf_scf_only"


def test_build_qmef_attachment_full_pipeline_extra(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference

    cfg = _h2_cfg(theory_level="full_pipeline")
    cfg.md_ml_export.include_hf_nuclear_gradient = True
    out = {"scf_energy": -1.1, "energy_after_variational": -1.2, "repro": {}}
    reference = MagicMock(spec=ClassicalMeanFieldReference)
    mock_rhf = MagicMock()
    mock_rhf.e_tot = -1.1
    mock_rhf.mol = MagicMock()
    mock_rhf.mol.atom = [(1, (0, 0, 0)), (1, (0, 0, 0.74))]

    def _runner(_child_cfg: ExperimentConfig, *, cfg_path: Path | None = None) -> dict:
        return {"energy_after_variational": -1.15, "repro": {}}

    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.as_pyscf_rhf",
        lambda _ref: mock_rhf,
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.primary_qmframe",
        lambda _cfg, _out, _rhf: _sample_frame(energy=-1.2),
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.rhf_at_coordinates",
        lambda _cfg, _coords: mock_rhf,
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.atomic_numbers_from_pyscf_mol",
        lambda _mol: [1, 1],
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.hf_nuclear_forces_neg_gradient_hartree_bohr",
        lambda _rhf, _method: [[0.0, 0.0, 0.1], [0.0, 0.0, -0.1]],
    )

    block = build_qmef_ml_attachment_repro_block(cfg, out, reference, pipeline_runner=_runner)
    assert len(block["dataset"]["frames"]) == 2
    assert block["frame_meta"][1]["energy_theory"] == "nested_full_pipeline"
    assert block["dataset"]["frames"][1]["forces_hartree_bohr"]


def test_build_qmef_attachment_context_and_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference

    cfg = _h2_cfg(extra_coords=[])
    out = {"repro": {}}
    reference = MagicMock(spec=ClassicalMeanFieldReference)
    frame = _sample_frame()

    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.as_pyscf_rhf",
        lambda _ref: MagicMock(),
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.primary_qmframe",
        lambda _cfg, _out, _rhf: frame,
    )

    ctx = QmefAttachmentContext(cfg=cfg, out=out, cfg_path=None)
    block_ctx = build_qmef_ml_attachment_from_context(ctx, reference)
    block_alias = build_qmef_dataset_single_frame_repro_block(cfg, out, reference)
    assert block_ctx["schema"] == block_alias["schema"] == QMEF_ML_ATTACHMENT_V1

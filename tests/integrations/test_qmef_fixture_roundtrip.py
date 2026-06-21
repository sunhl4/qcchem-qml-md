"""Golden QMEF extxyz fixture round-trip (export/import energy and geometry)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.md_bridge.exporter import export_extended_xyz
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame

pytestmark = pytest.mark.l1_md_ml


def _load_fixture_extxyz(path: Path) -> QMEFDataset:
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    n_atoms = int(lines[0])
    assert n_atoms == 2
    frames: list[QMFrame] = []
    i = 1
    while i < len(lines):
        comment = lines[i]
        frame_energy = -1.12
        if "energy=" in comment:
            for token in comment.split():
                if token.startswith("energy="):
                    frame_energy = float(token.split("=", 1)[1])
                    break
        i += 1
        positions: list[list[float]] = []
        for _ in range(n_atoms):
            parts = lines[i].split()
            positions.append([float(parts[1]), float(parts[2]), float(parts[3])])
            if len(parts) > 4 and "energy=" not in comment:
                frame_energy = float(parts[4])
            i += 1
        frames.append(
            QMFrame(
                atomic_numbers=[1, 1],
                positions_bohr=positions,
                energy_hartree=float(frame_energy),
                forces_hartree_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
                charge=0,
                multiplicity=1,
            )
        )
    return QMEFDataset(frames=frames)


def test_qmef_golden_extxyz_roundtrip(tmp_path: Path) -> None:
    fixture = Path(__file__).resolve().parent / "fixtures" / "qmef" / "h2_equilibrium.extxyz"
    dataset = _load_fixture_extxyz(fixture)
    out_path = tmp_path / "roundtrip.xyz"
    export_extended_xyz(dataset, out_path)
    roundtrip = _load_fixture_extxyz(out_path)
    assert len(roundtrip.frames) == len(dataset.frames)
    for orig, rt in zip(dataset.frames, roundtrip.frames, strict=True):
        assert rt.energy_hartree == pytest.approx(orig.energy_hartree)
        for pos_o, pos_r in zip(orig.positions_bohr, rt.positions_bohr, strict=True):
            assert pos_r == pytest.approx(pos_o)

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import (
    ExperimentConfig,
    load_cartesian_geometry_file,
    load_experiment_config,
    merge_molecule_dict_from_geometry_file,
    parse_xyz,
)
from qchem_stack.exceptions import ConfigurationError
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_parse_xyz_h2() -> None:
    text = """2
H2 bond
H  0.0  0.0  0.0
H  0.0  0.0  0.74
"""
    syms, coords = parse_xyz(text)
    assert syms == ["H", "H"]
    assert coords[0] == [0.0, 0.0, 0.0]
    assert coords[1][2] == pytest.approx(0.74)


def test_parse_xyz_extended_extra_columns() -> None:
    text = """1
comment
O   0.1  0.2  0.3   0  0  0  0  0  0
"""
    syms, coords = parse_xyz(text)
    assert syms == ["O"]
    assert coords[0] == pytest.approx([0.1, 0.2, 0.3])


def test_merge_molecule_rejects_inline_coordinates(tmp_path: Path) -> None:
    xyz = tmp_path / "a.xyz"
    xyz.write_text("1\nx\nH 0 0 0\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="geometry_file cannot be used together"):
        merge_molecule_dict_from_geometry_file(
            {"geometry_file": "a.xyz", "coordinates": [[0, 0, 0]]},
            base_dir=tmp_path,
        )


def test_load_experiment_config_geometry_file_relative(tmp_path: Path) -> None:
    geom = tmp_path / "sub" / "h2.xyz"
    geom.parent.mkdir(parents=True, exist_ok=True)
    geom.write_text(
        "2\nh2\nH 0 0 0\nH 0 0 0.74\n",
        encoding="utf-8",
    )
    cfg_yaml = tmp_path / "exp.yaml"
    cfg_yaml.write_text(
        """
schema_version: "2"
experiment_id: geom_file_test
random_seed: 0
molecule:
  geometry_file: sub/h2.xyz
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  strategy: cas
  cas:
    n_orbitals: 2
    n_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_yaml)
    assert cfg.molecule.symbols == ["H", "H"]
    assert len(cfg.molecule.coordinates) == 2
    assert cfg.molecule.coordinates[1][2] == pytest.approx(0.74)


def test_merge_optional_matching_symbols(tmp_path: Path) -> None:
    xyz = tmp_path / "x.xyz"
    xyz.write_text("1\nx\nO 0 0 0\n", encoding="utf-8")
    out = merge_molecule_dict_from_geometry_file(
        {"geometry_file": "x.xyz", "symbols": ["O"], "basis": "sto-3g"},
        base_dir=tmp_path,
    )
    assert out["symbols"] == ["O"]
    assert "geometry_file" not in out


def test_merge_symbols_mismatch(tmp_path: Path) -> None:
    xyz = tmp_path / "x.xyz"
    xyz.write_text("1\nx\nO 0 0 0\n", encoding="utf-8")
    with pytest.raises(ConfigurationError, match="disagrees"):
        merge_molecule_dict_from_geometry_file(
            {"geometry_file": "x.xyz", "symbols": ["N"]},
            base_dir=tmp_path,
        )


def test_load_cartesian_unknown_suffix_with_explicit_format(tmp_path: Path) -> None:
    p = tmp_path / "weird.geom"
    p.write_text("1\nx\nH 0 0 0\n", encoding="utf-8")
    syms, coords = load_cartesian_geometry_file(p, file_format="xyz")
    assert syms == ["H"]


def test_from_yaml_dict_geometry_files_base_dir(tmp_path: Path) -> None:
    xyz = tmp_path / "a.xyz"
    xyz.write_text("1\nx\nH 0 0 0\n", encoding="utf-8")
    cfg = ExperimentConfig.from_yaml_dict(
        {
            "schema_version": "2",
            "experiment_id": "g",
            "random_seed": 0,
            "molecule": {"geometry_file": "a.xyz", "basis": "sto-3g"},
            "scf": {"driver": "pyscf", "method": "RHF"},
            "active_space": {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
        },
        geometry_files_base_dir=tmp_path,
    )
    assert cfg.molecule.symbols == ["H"]


def test_pipeline_runs_with_geometry_file_config_when_pyscf_available() -> None:
    pytest.importorskip("pyscf")
    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_geometry_file_xyz.yaml"
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    assert float(out["scf_energy"]) < 0.0
    assert "pre_quantum_input" in out
    assert out["pre_quantum_input"]["schema"] == "pre_quantum_input_v1"

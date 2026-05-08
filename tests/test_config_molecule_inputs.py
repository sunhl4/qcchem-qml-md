from __future__ import annotations

import pytest

from qchem_stack.config import load_experiment_config


def test_density_fit_auxbasis_requires_density_fit(tmp_path) -> None:
    p = tmp_path / "bad_density_fit.yaml"
    p.write_text(
        """
schema_version: "1"
experiment_id: cfg_inputs_density_fit
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
  density_fit_auxbasis: weigend
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="density_fit_auxbasis requires scf.density_fit"):
        load_experiment_config(p)


def test_molecule_coordinates_and_zmatrix_mutually_exclusive(tmp_path) -> None:
    p = tmp_path / "bad_geom.yaml"
    p.write_text(
        """
schema_version: "1"
experiment_id: cfg_inputs_bad_geom
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  zmatrix: |
    H
    H 1 0.74
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="mutually exclusive"):
        load_experiment_config(p)

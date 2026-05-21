from __future__ import annotations

import pytest

from qchem_stack.config import load_experiment_config


def test_psi4_rejects_non_gamma_pbc_mesh(tmp_path) -> None:
    root = tmp_path
    cfg_path = root / "pbc.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: "pbc_mesh"
random_seed: 0
molecule:
  symbols: ["H"]
  coordinates:
    - [0.0, 0.0, 0.0]
  coordinate_unit: bohr
  charge: 0
  multiplicity: 1
  basis: "sto-3g"
scf:
  driver: "psi4"
  method: "RHF"
active_space:
  strategy: cas
  cas:
    n_orbitals: 1
    n_electrons: 1
chemistry_extended:
  pbc:
    enabled: true
    kmesh: [1, 1, 2]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="kmesh"):
        load_experiment_config(cfg_path)

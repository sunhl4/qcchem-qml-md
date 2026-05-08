from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config


def test_avas_with_psi4_mentions_capability_in_error(tmp_path: Path) -> None:
    cfg_path = tmp_path / "avas_psi4.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: avas_psi4_gate
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  basis: sto-3g
scf:
  driver: psi4
  method: RHF
active_space:
  strategy: avas
  n_active_orbitals: 2
  n_active_electrons: 2
chemistry_extended:
  avas_ao_labels: ["H 1s"]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="supports_avas_active_space_projection"):
        load_experiment_config(cfg_path)

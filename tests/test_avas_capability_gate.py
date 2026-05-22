from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.exceptions import ConfigurationError


def test_psi4_avas_config_loads_when_capability_true() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_psi4_avas.yaml")
    assert cfg.scf.driver == "psi4"
    assert cfg.active_space.strategy == "avas"
    assert cfg.chemistry_extended.avas.ao_labels


def test_precomputed_avas_rejected_by_capability(tmp_path: Path) -> None:
    cfg_path = tmp_path / "avas_precomputed.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: avas_precomputed_gate
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
  basis: sto-3g
scf:
  driver: precomputed
  method: RHF
  precomputed:
    bundle_path: configs/precomputed_classical_reference_h2.json
active_space:
  strategy: avas
  cas:
    n_orbitals: 2
    n_electrons: 2
chemistry_extended:
  avas:
    ao_labels: ["H 1s"]
""",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="supports_avas_active_space_projection"):
        load_experiment_config(cfg_path)

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver, active_space_casci_raw_blocks
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_active_space_casci_respects_frozen_orbitals_metadata() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    rhf = drv.run_rhf()
    c0, h10, _ = active_space_casci_raw_blocks(rhf, 1, 0)
    rhf_frozen = rhf
    rhf_frozen.driver_meta["active_space_frozen_orbitals"] = [0]
    c1, h11, _ = active_space_casci_raw_blocks(rhf_frozen, 1, 0)
    assert np.isfinite(c0) and np.isfinite(c1)
    assert h10.shape == (1, 1)
    assert h11.shape == (1, 1)


def test_pipeline_records_mo_coeff_transform_hook_metadata(tmp_path) -> None:
    cfg_path = tmp_path / "hook.yaml"
    cfg_path.write_text(
        """
schema_version: "2"
experiment_id: hook_meta
random_seed: 3
molecule:
  symbols: ["H", "H"]
  coordinates:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  coordinate_unit: bohr
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
backend:
  provider: statevector
quantum:
  algorithm: vqe
  vqe:
    depth: 1
    maxiter: 5
  pauli:
    use_protocol: false
chemistry_extended:
  mo_transform:
    hook: reverse_mo_columns
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    out = run_pipeline_sync(cfg, cfg_path=cfg_path)
    pd = (out["repro"]["parity_snapshot"]["hamiltonian_meta"] or {}).get("pyscf_driver") or {}
    assert (pd.get("mo_coeff_transform_hook_v1") or {}).get("hook") == "reverse_mo_columns"

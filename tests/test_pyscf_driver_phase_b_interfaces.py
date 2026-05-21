from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.config import load_experiment_config


def _h2_cfg_yaml() -> str:
    return """
schema_version: "2"
experiment_id: h2_phase_b_if
random_seed: 0
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
"""


def test_get_system_ao_without_global_hf(tmp_path) -> None:
    p = tmp_path / "h2.yaml"
    p.write_text(_h2_cfg_yaml(), encoding="utf-8")
    cfg = load_experiment_config(p)
    drv = PySCFDriver.from_config(cfg)
    ao = drv.get_system_ao(run_hf=False)
    assert ao.has_run_hf is False
    assert ao.e_tot is None
    assert ao.driver_meta.get("integral_representation") == "ao"
    assert ao.driver_meta.get("ao_run_hf") is False
    assert hasattr(ao.mf, "kernel")


def test_get_lowdin_system_shapes(tmp_path) -> None:
    p = tmp_path / "h2.yaml"
    p.write_text(_h2_cfg_yaml(), encoding="utf-8")
    cfg = load_experiment_config(p)
    drv = PySCFDriver.from_config(cfg)
    low = drv.get_lowdin_system()
    n = low.h1_spatial.shape[0]
    assert low.h1_spatial.shape == (n, n)
    assert low.rdm1_spatial.shape == (n, n)
    assert low.h2_spatial.shape == (n, n, n, n)
    assert low.driver_meta.get("integral_representation") == "lowdin_orth_ao"
    # Numerical sanity: symmetric one-body and finite arrays.
    assert np.allclose(low.h1_spatial, low.h1_spatial.T, atol=1e-8)
    assert np.isfinite(low.h1_spatial).all()
    assert np.isfinite(low.h2_spatial).all()
    assert np.isfinite(low.rdm1_spatial).all()

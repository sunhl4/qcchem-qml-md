"""PySCF AO / Löwdin system views via :mod:`qchem_stack.chem.systems.pyscf_factory`."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.systems.pyscf_factory import (
    pyscf_ao_system_from_config,
    pyscf_lowdin_system_from_rhf,
)
from qchem_stack.config import load_experiment_config
from tests.fixtures.classical_reference import pyscf_rhf_from_config


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


def test_pyscf_ao_system_without_global_hf(tmp_path) -> None:
    p = tmp_path / "h2.yaml"
    p.write_text(_h2_cfg_yaml(), encoding="utf-8")
    cfg = load_experiment_config(p)
    ao = pyscf_ao_system_from_config(cfg, run_hf=False)
    assert ao.has_run_hf is False
    assert ao.e_tot is None
    assert ao.driver_meta.get("integral_representation") == "ao"
    assert ao.driver_meta.get("ao_run_hf") is False
    assert hasattr(ao.mf, "kernel")


def test_pyscf_lowdin_system_shapes(tmp_path) -> None:
    p = tmp_path / "h2.yaml"
    p.write_text(_h2_cfg_yaml(), encoding="utf-8")
    cfg = load_experiment_config(p)
    low = pyscf_lowdin_system_from_rhf(pyscf_rhf_from_config(cfg))
    n = low.h1_spatial.shape[0]
    assert low.h1_spatial.shape == (n, n)
    assert low.rdm1_spatial.shape == (n, n)
    assert low.h2_spatial.shape == (n, n, n, n)
    assert low.driver_meta.get("integral_representation") == "lowdin_orth_ao"
    assert np.allclose(low.h1_spatial, low.h1_spatial.T, atol=1e-8)
    assert np.isfinite(low.h1_spatial).all()
    assert np.isfinite(low.h2_spatial).all()
    assert np.isfinite(low.rdm1_spatial).all()

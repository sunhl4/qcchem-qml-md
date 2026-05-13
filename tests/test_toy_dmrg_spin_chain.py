from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_toy_module():
    root = Path(__file__).resolve().parents[1]
    path = root / "examples" / "toy_dmrg_spin_chain.py"
    name = "qchem_examples_toy_dmrg_spin_chain"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # Dynamic modules must be registered for dataclasses/typing to resolve `__module__`.
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_toy_dmrg_matches_exact_small_chain():
    mod = _load_toy_module()
    L = 8
    exact = mod.exact_heisenberg_obc_energy(L, j=1.0, jz=1.0)
    res = mod.run_toy_dmrg(chain_length=L, m_warmup=20, m_sweep_list=[20, 30], j=1.0, jz=1.0, verbose=False)
    assert abs(res.energy - exact) < 1e-6


def test_exact_two_site_heisenberg_ground_state():
    mod = _load_toy_module()
    e2 = mod.exact_heisenberg_obc_energy(2, j=1.0, jz=1.0)
    assert abs(e2 - (-0.75)) < 1e-10

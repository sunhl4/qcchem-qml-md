"""Psi4 vs PySCF H2 sto-3g active-space integral parity (optional dependency)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.scf_stage import run_scf_reference

# Soft thresholds documented in chem.integrals.psi4_active_space module docstring.
PSI4_PYSCF_H2_CONSTANT_ATOL = 5e-3
PSI4_PYSCF_H2_H1_MAX_ABS_ATOL = 5e-2
PSI4_PYSCF_H2_H2_MAX_ABS_ATOL = 8e-2


def _h2_cfg_pyscf(root: Path):
    return load_experiment_config(root / "configs" / "example_h2.yaml")


@pytest.mark.psi4
@pytest.mark.pyscf
def test_psi4_pyscf_h2_canonical_pack_constant_near_parity() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    cfg_py = _h2_cfg_pyscf(root)
    cfg_psi = cfg_py.model_copy(update={"scf": cfg_py.scf.model_copy(update={"driver": "psi4"})})
    ref_py = run_scf_reference(cfg_py)
    ref_psi = run_scf_reference(cfg_psi)
    na = int(cfg_py.active_space.n_active_orbitals)
    ne = int(cfg_py.active_space.n_active_electrons)
    pack_py = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        ref_py, n_active_orbitals=na, n_active_electrons=ne
    )
    pack_psi = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        ref_psi, n_active_orbitals=na, n_active_electrons=ne
    )
    c_py = float(pack_py.compact.constant)
    c_psi = float(pack_psi.compact.constant)
    assert abs(c_py - c_psi) < PSI4_PYSCF_H2_CONSTANT_ATOL
    h1_py = np.asarray(pack_py.compact.h1_active_mo, dtype=float)
    h1_psi = np.asarray(pack_psi.compact.h1_active_mo, dtype=float)
    assert h1_py.shape == h1_psi.shape
    assert float(np.max(np.abs(h1_py - h1_psi))) < PSI4_PYSCF_H2_H1_MAX_ABS_ATOL
    h2_py = np.asarray(pack_py.compact.eri_active_mo_compact, dtype=float)
    h2_psi = np.asarray(pack_psi.compact.eri_active_mo_compact, dtype=float)
    assert h2_py.shape == h2_psi.shape
    assert float(np.max(np.abs(h2_py - h2_psi))) < PSI4_PYSCF_H2_H2_MAX_ABS_ATOL


@pytest.mark.psi4
@pytest.mark.pyscf
def test_psi4_pyscf_pre_quantum_build_finite_energies() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    cfg_py = _h2_cfg_pyscf(root)
    cfg_psi = cfg_py.model_copy(update={"scf": cfg_py.scf.model_copy(update={"driver": "psi4"})})
    p_py = build_pre_quantum_input(cfg_py, run_scf_reference(cfg_py), cfg_path=root / "configs" / "example_h2.yaml")
    p_psi = build_pre_quantum_input(cfg_psi, run_scf_reference(cfg_psi))
    assert p_py.qubit_hamiltonian.n_qubits == p_psi.qubit_hamiltonian.n_qubits
    assert float((p_py.qubit_hamiltonian.meta or {})["scf_energy_au"]) < 0.0
    assert float((p_psi.qubit_hamiltonian.meta or {})["scf_energy_au"]) < 0.0
    assert str((p_py.qubit_hamiltonian.meta or {}).get("hamiltonian_fingerprint") or "")
    assert str((p_psi.qubit_hamiltonian.meta or {}).get("hamiltonian_fingerprint") or "")

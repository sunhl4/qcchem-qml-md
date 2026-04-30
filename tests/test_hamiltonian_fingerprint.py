"""Hamiltonian fingerprint stability (minimal PySCF for H2)."""

from __future__ import annotations

from pathlib import Path

import pytest
from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import hamiltonian_fingerprint_from_qubit_operator


def test_fingerprint_stable_for_same_operator() -> None:
    q = QubitOperator("Z0", 0.5) + QubitOperator("X0 Z1", -0.25)
    a, trunc_a = hamiltonian_fingerprint_from_qubit_operator(q)
    b, trunc_b = hamiltonian_fingerprint_from_qubit_operator(q)
    assert a == b
    assert not trunc_a and not trunc_b


def test_fingerprint_changes_with_coefficient() -> None:
    q1 = QubitOperator("Z0", 1.0)
    q2 = QubitOperator("Z0", 1.0000001)
    a, _ = hamiltonian_fingerprint_from_qubit_operator(q1)
    b, _ = hamiltonian_fingerprint_from_qubit_operator(q2)
    assert a != b


def test_fingerprint_truncation_flag() -> None:
    q = QubitOperator("Z0", 1.0) + QubitOperator("Z1", 2.0) + QubitOperator("X0", 3.0)
    _, trunc = hamiltonian_fingerprint_from_qubit_operator(q, max_terms=2)
    assert trunc is True
    full, trunc2 = hamiltonian_fingerprint_from_qubit_operator(q)
    assert trunc2 is False


def test_h2_molecular_hamiltonian_fingerprint_stable() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.config import load_experiment_config
    from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
    from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_pyscf

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    r = drv.run_rhf()
    h1 = molecular_hamiltonian_from_pyscf(
        r,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
    )
    r2 = drv.run_rhf()
    h2 = molecular_hamiltonian_from_pyscf(
        r2,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
    )
    fp1 = h1.meta["hamiltonian_fingerprint"]
    fp2 = h2.meta["hamiltonian_fingerprint"]
    assert fp1 == fp2
    assert len(fp1) == 32
    assert not h1.meta.get("hamiltonian_fingerprint_truncated")


def test_h2_fingerprint_sensitive_to_active_electrons() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.config import load_experiment_config
    from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
    from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_pyscf

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    r = drv.run_rhf()
    if cfg.active_space.n_active_electrons < 2:
        pytest.skip("need n_active_electrons >= 2 to compare")
    h_same = molecular_hamiltonian_from_pyscf(
        r,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=cfg.active_space.n_active_electrons,
    )
    # Different electron count in fermion_space / integrals → different operator
    h_diff = molecular_hamiltonian_from_pyscf(
        r,
        n_active_orbitals=cfg.active_space.n_active_orbitals,
        n_active_electrons=max(1, cfg.active_space.n_active_electrons - 1),
    )
    assert h_same.meta["hamiltonian_fingerprint"] != h_diff.meta["hamiltonian_fingerprint"]


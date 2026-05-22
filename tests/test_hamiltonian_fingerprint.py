"""Hamiltonian fingerprint stability (minimal PySCF for H2)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from openfermion import InteractionOperator
from openfermion.ops import QubitOperator

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import hamiltonian_fingerprint_from_qubit_operator
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import load_experiment_config
from tests.fixtures.classical_reference import pyscf_rhf_from_config


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

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    r = pyscf_rhf_from_config(cfg)
    ref1 = ClassicalMeanFieldReference(
        mf=r.mf,
        e_tot=float(r.e_tot),
        mo_energy=r.mo_energy,
        molecular_system=r.molecular_system,
        driver_meta=dict(r.driver_meta),
    )
    h1 = build_pre_quantum_input(cfg, ref1).qubit_hamiltonian
    r2 = pyscf_rhf_from_config(cfg)
    ref2 = ClassicalMeanFieldReference(
        mf=r2.mf,
        e_tot=float(r2.e_tot),
        mo_energy=r2.mo_energy,
        molecular_system=r2.molecular_system,
        driver_meta=dict(r2.driver_meta),
    )
    h2 = build_pre_quantum_input(cfg, ref2).qubit_hamiltonian
    fp1 = h1.meta["hamiltonian_fingerprint"]
    fp2 = h2.meta["hamiltonian_fingerprint"]
    assert fp1 == fp2
    assert len(fp1) == 32
    assert not h1.meta.get("hamiltonian_fingerprint_truncated")


def test_h2_fingerprint_sensitive_to_fermion_mapping() -> None:
    pytest.importorskip("pyscf")

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    r = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=r.mf,
        e_tot=float(r.e_tot),
        mo_energy=r.mo_energy,
        molecular_system=r.molecular_system,
        driver_meta=dict(r.driver_meta),
    )
    h_jw = build_pre_quantum_input(cfg, ref).qubit_hamiltonian
    cfg_bk = cfg.model_copy(
        update={
            "active_space": cfg.active_space.model_copy(
                update={
                    "mapping": cfg.active_space.mapping.model_copy(
                        update={"fermion_qubit": "bravyi_kitaev"}
                    )
                }
            )
        }
    )
    h_bk = build_pre_quantum_input(cfg_bk, ref).qubit_hamiltonian
    assert h_jw.meta["hamiltonian_fingerprint"] != h_bk.meta["hamiltonian_fingerprint"]


def test_non_pyscf_reference_meta_stored_as_classical_driver() -> None:
    from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_active_space_fermionic_operator

    mol_op = InteractionOperator(
        0.0,
        np.zeros((2, 2), dtype=float),
        np.zeros((2, 2, 2, 2), dtype=float),
    )
    fs = FermionSpace(n_spin_orbitals=2, n_electrons=2)
    ref = ClassicalMeanFieldReference(
        mf=None,
        e_tot=0.0,
        mo_energy=np.zeros(1, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"], coordinates_bohr=np.zeros((1, 3), dtype=float)
        ),
        driver_meta={"upstream_classical_software_tag": "mock_solver", "note": "contract-test"},
    )
    qh = qubit_hamiltonian_from_active_space_fermionic_operator(
        mol_op,
        fs,
        n_active_orbitals=1,
        n_active_electrons=2,
        rhf=ref,
    )
    assert "classical_driver" in qh.meta
    assert (
        qh.meta.get("classical_driver", {}).get("upstream_classical_software_tag") == "mock_solver"
    )
    assert qh.meta.get("integral_source") == "mock_solver_active_space"
    assert (
        qh.meta.get("integral_openfermion_bridge")
        == "mock_solver_openfermion_interaction_operator_v1"
    )


def test_canonical_pack_provenance_controls_integral_metadata() -> None:
    from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_active_space_fermionic_operator

    mol_op = InteractionOperator(
        0.0,
        np.zeros((2, 2), dtype=float),
        np.zeros((2, 2, 2, 2), dtype=float),
    )
    fs = FermionSpace(n_spin_orbitals=2, n_electrons=2)
    pack = CanonicalActiveSpaceIntegralPack(
        compact=object(),
        provenance={
            "upstream_integral_source": "stub_backend_active_space_pack_v1",
            "integral_openfermion_bridge": "stub_openfermion_bridge_v1",
            "classical_backend": "stub_backend",
        },
    )
    qh = qubit_hamiltonian_from_active_space_fermionic_operator(
        mol_op,
        fs,
        n_active_orbitals=1,
        n_active_electrons=2,
        canonical_pack=pack,
    )
    assert qh.meta.get("integral_source") == "stub_backend_active_space_pack_v1"
    assert qh.meta.get("integral_openfermion_bridge") == "stub_openfermion_bridge_v1"


def test_explicit_integral_metadata_overrides_pack_provenance() -> None:
    from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_active_space_fermionic_operator

    mol_op = InteractionOperator(
        0.0,
        np.zeros((2, 2), dtype=float),
        np.zeros((2, 2, 2, 2), dtype=float),
    )
    fs = FermionSpace(n_spin_orbitals=2, n_electrons=2)
    pack = CanonicalActiveSpaceIntegralPack(
        compact=object(),
        provenance={
            "upstream_integral_source": "pack_source_v1",
            "integral_openfermion_bridge": "pack_bridge_v1",
        },
    )

    qh = qubit_hamiltonian_from_active_space_fermionic_operator(
        mol_op,
        fs,
        n_active_orbitals=1,
        n_active_electrons=2,
        canonical_pack=pack,
        integral_source="explicit_source_v1",
        integral_openfermion_bridge="explicit_bridge_v1",
    )

    assert qh.meta["integral_source"] == "explicit_source_v1"
    assert qh.meta["integral_openfermion_bridge"] == "explicit_bridge_v1"


def test_compact_non_jw_path_forwards_explicit_integral_metadata() -> None:
    from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_compact_restricted_active_space

    class _Compact:
        n_active_orbitals = 1
        n_active_electrons = 2
        constant = 0.0
        h1_active_mo = np.zeros((1, 1), dtype=float)

        def dense_h2_chemist_spatial(self) -> np.ndarray:
            return np.zeros((1, 1, 1, 1), dtype=float)

        def to_interaction_operator(self) -> InteractionOperator:
            return InteractionOperator(
                0.0,
                np.zeros((2, 2), dtype=float),
                np.zeros((2, 2, 2, 2), dtype=float),
            )

    fs = FermionSpace(n_spin_orbitals=2, n_electrons=2)
    qh = qubit_hamiltonian_from_compact_restricted_active_space(
        _Compact(),
        fs,
        n_active_orbitals=1,
        n_active_electrons=2,
        fermion_qubit_mapping="bravyi_kitaev",
        integral_source="compact_explicit_source_v1",
        integral_openfermion_bridge="compact_explicit_bridge_v1",
    )

    assert qh.meta["integral_source"] == "compact_explicit_source_v1"
    assert qh.meta["integral_openfermion_bridge"] == "compact_explicit_bridge_v1"

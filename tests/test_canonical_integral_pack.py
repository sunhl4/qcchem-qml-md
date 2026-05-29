"""Canonical active-space integral pack interchange (PySCF reference path)."""

from __future__ import annotations

import pytest

from tests.fixtures.classical_reference import pyscf_rhf_from_config
from tests.helpers.paths import configs_path


def test_pack_roundtrip_matches_unified_hamiltonian_entrypoint() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_canonical_active_space_pack
    from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
    from qchem_stack.config import load_experiment_config

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    na = cfg.active_space.cas.n_orbitals
    ne = cfg.active_space.cas.n_electrons
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    pack = CanonicalActiveSpaceIntegralPack.from_pyscf_reference(
        rhf, n_active_orbitals=na, n_active_electrons=ne
    )
    assert pack.provenance.get("upstream_integral_source") == "pyscf_casci_h2eff_compact"
    assert pack.provenance.get("integral_openfermion_bridge") == "pyscf_spatial_openfermion_v1"
    q_pack = molecular_hamiltonian_from_canonical_active_space_pack(
        pack,
        n_active_orbitals=na,
        n_active_electrons=ne,
        fermion_qubit_mapping=cfg.active_space.mapping.fermion_qubit,
        classical_reference_for_meta=ref,
    )
    q_ref = build_pre_quantum_input(cfg, ref).hamiltonian
    assert q_ref.meta["hamiltonian_fingerprint"] == q_pack.meta["hamiltonian_fingerprint"]
    assert q_pack.meta.get("canonical_integral_pack", {}).get("schema")
    assert q_pack.meta.get("integral_source") == pack.provenance.get("upstream_integral_source")
    assert q_pack.meta.get("integral_openfermion_bridge") == pack.provenance.get(
        "integral_openfermion_bridge"
    )


def test_psi4_solver_supports_restricted_active_space_hamiltonian() -> None:
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver
    from qchem_stack.config import load_experiment_config

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    cfg.scf.driver = "psi4"  # type: ignore[misc]
    sol = Psi4IntegralSolver.from_experiment_config(cfg)
    assert sol.capabilities.supports_restricted_active_space_qubit_hamiltonian


def test_classical_reference_fermionic_operator_matches_canonical_pack() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import (
        fermionic_active_space_interaction_operator_from_canonical_pack,
        fermionic_active_space_interaction_operator_from_classical_reference,
    )
    from qchem_stack.config import load_experiment_config

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    na = cfg.active_space.cas.n_orbitals
    ne = cfg.active_space.cas.n_electrons
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    pack = CanonicalActiveSpaceIntegralPack.from_classical_reference(
        ref,
        n_active_orbitals=na,
        n_active_electrons=ne,
    )
    op_legacy, fs_legacy = fermionic_active_space_interaction_operator_from_canonical_pack(pack)
    op_ref, fs_ref = fermionic_active_space_interaction_operator_from_classical_reference(
        ref,
        n_active_orbitals=na,
        n_active_electrons=ne,
    )
    assert fs_ref.n_spin_orbitals == fs_legacy.n_spin_orbitals
    assert fs_ref.n_electrons == fs_legacy.n_electrons
    assert op_ref.one_body_tensor.shape == op_legacy.one_body_tensor.shape
    assert op_ref.two_body_tensor.shape == op_legacy.two_body_tensor.shape

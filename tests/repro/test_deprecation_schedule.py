"""Removed APIs must not be importable from deprecated paths (v0.8 + v1.0)."""

from __future__ import annotations

import importlib

import pytest


def test_integrations_dmet_self_consistent_shim_removed() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("qchem_stack.integrations.dmet_self_consistent")


def test_apply_backend_profile_removed() -> None:
    from qchem_stack.backends import profiles

    assert not hasattr(profiles, "apply_backend_profile")


def test_molecular_hamiltonian_from_classical_reference_removed() -> None:
    from qchem_stack.chem import hamiltonian_build

    assert not hasattr(hamiltonian_build, "molecular_hamiltonian_from_classical_reference")


def test_schmidt_variational_sidecar_module_removed_v1() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("qchem_stack.chem.embedding.schmidt_variational_sidecar")


def test_molecular_hamiltonian_from_pyscf_removed_v1() -> None:
    from qchem_stack.chem import hamiltonian

    assert not hasattr(hamiltonian, "molecular_hamiltonian_from_pyscf")


def test_pre_quantum_build_hamiltonian_alias_removed_v1() -> None:
    from qchem_stack.chem import pre_quantum_build

    assert not hasattr(pre_quantum_build, "hamiltonian")


def test_projection_hamiltonian_mulliken_shim_removed_v1() -> None:
    from qchem_stack.chem.embedding import projection_hamiltonian

    assert not hasattr(projection_hamiltonian, "mulliken_mo_populations_on_atoms")

"""Deprecation warnings for chem-layer lazy shims."""

from __future__ import annotations

import importlib
import warnings


def test_schmidt_variational_sidecar_emits_deprecation_warning() -> None:
    mod = importlib.import_module("qchem_stack.chem.embedding.schmidt_variational_sidecar")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        _ = mod.run_schmidt_per_fragment_vqe
    assert any(
        issubclass(w.category, DeprecationWarning)
        and "integrations.schmidt_per_fragment_vqe" in str(w.message)
        for w in caught
    )


def test_embedding_exports_vqe_solver_directly() -> None:
    mod = importlib.import_module("qchem_stack.chem.embedding")
    from qchem_stack.chem.embedding.fragment_solvers.qubit_hamiltonian_vqe import (
        QubitHamiltonianFragmentSolverVQE,
    )

    assert mod.QubitHamiltonianFragmentSolverVQE is QubitHamiltonianFragmentSolverVQE

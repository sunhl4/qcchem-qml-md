"""Deprecation warnings for chem-layer lazy shims moved to integrations."""

from __future__ import annotations

import importlib
import warnings

import pytest


def test_embedding_lazy_vqe_solver_emits_deprecation_warning() -> None:
    mod = importlib.import_module("qchem_stack.chem.embedding")
    with pytest.warns(DeprecationWarning, match="integrations.dmet_fragment_solvers"):
        _ = mod.QubitHamiltonianFragmentSolverVQE


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

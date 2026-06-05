"""v1.0 removed embedding shims."""

from __future__ import annotations

import importlib

import pytest


def test_schmidt_variational_sidecar_module_removed() -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("qchem_stack.chem.embedding.schmidt_variational_sidecar")

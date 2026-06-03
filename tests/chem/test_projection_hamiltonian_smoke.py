"""Projection Hamiltonian builder import and capability preconditions."""

from __future__ import annotations

import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.embedding.projection_hamiltonian import (
    molecular_hamiltonian_fragment_mulliken_projection,
)
from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path


def test_projection_mulliken_config_loads() -> None:
    cfg = load_experiment_config(configs_path("example_h4_projection_mulliken.yaml"))
    assert cfg.embedding.mode.value == "projection"


def test_projection_requires_rhf_method() -> None:
    cfg = load_experiment_config(configs_path("example_h4_projection_mulliken.yaml"))
    cfg.scf.method = "UHF"
    from qchem_stack.exceptions import EmbeddingError

    class _Ref:
        def backend_tag(self) -> str:
            return "pyscf"

    with pytest.raises(EmbeddingError, match="RHF"):
        molecular_hamiltonian_fragment_mulliken_projection(_Ref(), cfg)  # type: ignore[arg-type]

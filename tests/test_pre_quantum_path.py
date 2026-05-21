"""Branch resolution for pre-quantum assembly (config / build / parity alignment)."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.chem.embedding.hamiltonian_semantics import pre_quantum_hamiltonian_semantics
from qchem_stack.chem.pre_quantum_path import (
    PreQuantumPath,
    pre_quantum_path_source,
    resolve_pre_quantum_path,
)
from qchem_stack.config import ExperimentConfig, load_experiment_config
from tests.embedding_nested import embedding_dmet


def _cfg(**embedding: object) -> ExperimentConfig:
    root = Path(__file__).resolve().parents[1]
    base = load_experiment_config(root / "configs" / "example_h2.yaml")
    if not embedding:
        return base
    return base.model_copy(update={"embedding": embedding_dmet(**embedding)})


def test_resolve_canonical_default_h2() -> None:
    cfg = _cfg()
    assert resolve_pre_quantum_path(cfg) == PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK
    assert (
        pre_quantum_path_source(resolve_pre_quantum_path(cfg))
        == "canonical_active_space_integral_pack"
    )


def test_resolve_precomputed_driver() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_precomputed_bundle.yaml")
    assert resolve_pre_quantum_path(cfg) == PreQuantumPath.PRECOMPUTED_BUNDLE


def test_resolve_embedding_plugin() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_decomposition_plugin_toy.yaml")
    assert resolve_pre_quantum_path(cfg) == PreQuantumPath.EMBEDDING_PLUGIN


def test_resolve_schmidt_atomic_production() -> None:
    cfg = _cfg(
        hamiltonian_source="schmidt_atomic_production",
        schmidt={"fragment_atom_indices": [0]},
    )
    assert resolve_pre_quantum_path(cfg) == PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION


def test_resolve_projection_fragment_mulliken_mo() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h4_projection_mulliken.yaml")
    assert resolve_pre_quantum_path(cfg) == PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO


def test_schmidt_takes_priority_over_projection_mode() -> None:
    """DMET + schmidt_atomic_production resolves to Schmidt even when mode is not projection."""
    cfg = _cfg(
        hamiltonian_source="schmidt_atomic_production",
        schmidt={"fragment_atom_indices": [0]},
    )
    assert resolve_pre_quantum_path(cfg) == PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION


def test_plugin_takes_priority_over_canonical() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_decomposition_plugin_toy.yaml")
    assert resolve_pre_quantum_path(cfg) == PreQuantumPath.EMBEDDING_PLUGIN


@pytest.mark.parametrize(
    ("yaml_name", "expected"),
    [
        ("example_h2.yaml", PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK),
        ("example_h2_precomputed_bundle.yaml", PreQuantumPath.PRECOMPUTED_BUNDLE),
        ("example_decomposition_plugin_toy.yaml", PreQuantumPath.EMBEDDING_PLUGIN),
        ("example_h4_projection_mulliken.yaml", PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO),
    ],
)
def test_semantics_branch_matches_resolve(yaml_name: str, expected: PreQuantumPath) -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / yaml_name)
    sem = pre_quantum_hamiltonian_semantics(cfg)
    assert sem["hamiltonian_branch"] == expected.value
    assert sem["hamiltonian_branch"] == resolve_pre_quantum_path(cfg).value

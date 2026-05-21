"""Nested embedding fixtures for tests (no flat YAML compatibility)."""

from __future__ import annotations

from typing import Any

from qchem_stack.config.embedding_specs import (
    EmbeddingDmet,
    EmbeddingNone,
    EmbeddingPlugin,
    EmbeddingProjection,
)

EmbeddingSpec = EmbeddingNone | EmbeddingDmet | EmbeddingProjection | EmbeddingPlugin


def embedding_none() -> EmbeddingNone:
    return EmbeddingNone.model_validate({"mode": "none"})


def embedding_dmet(
    *,
    fragment_labels: list[str] | None = None,
    hamiltonian_source: str = "parity_stub",
    schmidt: dict[str, Any] | None = None,
    fragment_solver: dict[str, Any] | None = None,
    uniform_multifragment_toy: bool = False,
    multifragment_one_shot_shared_hamiltonian: bool = False,
    target_fragment_electrons: int | None = None,
    n_scf_cycles_embedding: int | None = None,
    classical_reference_method: str | None = None,
) -> EmbeddingDmet:
    dmet: dict[str, Any] = {"hamiltonian_source": hamiltonian_source}
    if fragment_labels is not None:
        dmet["fragment_labels"] = fragment_labels
    if schmidt:
        dmet["schmidt"] = schmidt
    if fragment_solver:
        dmet["fragment_solver"] = fragment_solver
    if uniform_multifragment_toy:
        dmet["uniform_multifragment_toy"] = True
    if multifragment_one_shot_shared_hamiltonian:
        dmet["multifragment_one_shot_shared_hamiltonian"] = True
    if target_fragment_electrons is not None:
        dmet["target_fragment_electrons"] = target_fragment_electrons
    payload: dict[str, Any] = {"mode": "dmet", "dmet": dmet}
    if n_scf_cycles_embedding is not None:
        payload["n_scf_cycles_embedding"] = n_scf_cycles_embedding
    if classical_reference_method is not None:
        payload["classical_reference_method"] = classical_reference_method
    return EmbeddingDmet.model_validate(payload)


def schmidt_embedding_dmet(
    *,
    fragment_labels: list[str],
    hamiltonian_source: str = "schmidt_atomic_production",
    **schmidt: Any,
) -> EmbeddingDmet:
    """DMET + Schmidt block using nested field names only."""
    return embedding_dmet(
        fragment_labels=fragment_labels,
        hamiltonian_source=hamiltonian_source,
        schmidt=schmidt,
    )


def embedding_projection(
    *,
    quantum_hamiltonian: str = "global_active_space",
    fragment_atom_indices: list[int] | None = None,
    low_level: str | None = None,
    high_level: str | None = None,
    threshold: float | None = None,
) -> EmbeddingProjection:
    projection: dict[str, Any] = {"quantum_hamiltonian": quantum_hamiltonian}
    if fragment_atom_indices is not None:
        projection["fragment_atom_indices"] = fragment_atom_indices
    if low_level is not None:
        projection["low_level"] = low_level
    if high_level is not None:
        projection["high_level"] = high_level
    if threshold is not None:
        projection["threshold"] = threshold
    return EmbeddingProjection.model_validate({"mode": "projection", "projection": projection})

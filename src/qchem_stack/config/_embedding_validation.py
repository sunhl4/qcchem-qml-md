"""Cross-field validation helpers for :mod:`qchem_stack.config.embedding`."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .embedding import EmbeddingSpec


def nonempty_fragment_labels(labels: list[str]) -> list[str]:
    return [label for label in labels if str(label).strip()]


def validate_dmet_hamiltonian_source(spec: EmbeddingSpec) -> None:
    if spec.dmet_hamiltonian_source == "whole_active_system":
        _validate_whole_active_system(spec)
    if spec.dmet_hamiltonian_source == "schmidt_atomic_production":
        _validate_schmidt_atomic_production(spec)
    if (
        spec.dmet_uniform_multifragment_toy
        and spec.dmet_hamiltonian_source == "schmidt_atomic_production"
    ):
        raise ValueError(
            "dmet_uniform_multifragment_toy cannot be combined with schmidt_atomic_production."
        )
    if spec.schmidt_run_mu_bisection and spec.dmet_target_fragment_electrons is None:
        raise ValueError(
            "schmidt_run_mu_bisection requires embedding.dmet_target_fragment_electrons."
        )


def _validate_whole_active_system(spec: EmbeddingSpec) -> None:
    if spec.mode != "dmet":
        raise ValueError(
            "embedding.dmet_hamiltonian_source='whole_active_system' requires embedding.mode='dmet'."
        )
    labels = nonempty_fragment_labels(spec.fragment_labels)
    if spec.dmet_multifragment_one_shot_shared_hamiltonian:
        if len(labels) < 2:
            raise ValueError(
                "embedding.dmet_multifragment_one_shot_shared_hamiltonian requires at least two "
                "non-empty embedding.fragment_labels entries."
            )
    elif len(labels) != 1:
        raise ValueError(
            "embedding.dmet_hamiltonian_source='whole_active_system' requires exactly one "
            "non-empty embedding.fragment_labels entry (unless "
            "dmet_multifragment_one_shot_shared_hamiltonian is True)."
        )


def _validate_schmidt_atomic_production(spec: EmbeddingSpec) -> None:
    if spec.mode != "dmet":
        raise ValueError(
            "embedding.dmet_hamiltonian_source='schmidt_atomic_production' requires embedding.mode='dmet'."
        )
    if spec.schmidt_multi_fragment_atom_groups:
        _validate_multi_fragment_groups(spec)
    elif not spec.schmidt_fragment_atom_indices:
        raise ValueError(
            "schmidt_atomic_production requires non-empty embedding.schmidt_fragment_atom_indices "
            "when schmidt_multi_fragment_atom_groups is empty."
        )
    if spec.schmidt_n_bath_spatial < 1:
        raise ValueError("schmidt_n_bath_spatial must be at least 1.")
    if spec.schmidt_max_impurity_spatial_orbitals < 2:
        raise ValueError("schmidt_max_impurity_spatial_orbitals must be at least 2.")


def _validate_multi_fragment_groups(spec: EmbeddingSpec) -> None:
    if spec.schmidt_fragment_atom_indices:
        raise ValueError(
            "Use either embedding.schmidt_fragment_atom_indices (single fragment) or "
            "schmidt_multi_fragment_atom_groups, not both."
        )
    groups = spec.schmidt_multi_fragment_atom_groups
    if any(not group for group in groups):
        raise ValueError("schmidt_multi_fragment_atom_groups: each inner list must be non-empty")
    labels = nonempty_fragment_labels(spec.fragment_labels)
    if labels and len(labels) != len(groups):
        raise ValueError(
            "When schmidt_multi_fragment_atom_groups is set, embedding.fragment_labels "
            "must have the same length as groups (or be empty)."
        )
    if spec.schmidt_multi_primary_fragment_index >= len(groups):
        raise ValueError("schmidt_multi_primary_fragment_index is out of range for fragment groups")


def validate_plugin_embedding_requires_fields(spec: EmbeddingSpec) -> None:
    if spec.mode != "plugin":
        return
    if not (spec.decomposition_plugin or "").strip():
        raise ValueError("embedding.mode='plugin' requires embedding.decomposition_plugin")
    if not (spec.decomposition_plugin_json_path or "").strip():
        raise ValueError(
            "embedding.mode='plugin' requires embedding.decomposition_plugin_json_path"
        )


def validate_projection_mulliken_requires_mode_and_indices(spec: EmbeddingSpec) -> None:
    if spec.projection_quantum_hamiltonian != "fragment_mulliken_mo":
        return
    if spec.mode != "projection":
        raise ValueError(
            "embedding.projection_quantum_hamiltonian='fragment_mulliken_mo' requires embedding.mode='projection'."
        )
    if not spec.projection_fragment_atom_indices:
        raise ValueError(
            "embedding.projection_quantum_hamiltonian='fragment_mulliken_mo' requires non-empty "
            "embedding.projection_fragment_atom_indices."
        )

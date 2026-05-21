"""Cross-field validation helpers for :mod:`qchem_stack.config.embedding`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from qchem_stack.exceptions import ConfigurationError

from .embedding_enums import DmetHamiltonianSource, ProjectionQuantumHamiltonian
from .embedding_specs import EmbeddingDmet, EmbeddingNone, EmbeddingPlugin, EmbeddingProjection

if TYPE_CHECKING:
    from qchem_stack.chem.solvers.base import SolverCapabilities

EmbeddingSpec = EmbeddingNone | EmbeddingDmet | EmbeddingProjection | EmbeddingPlugin


SCHMIDT_DMET_MAX_CYCLES_LIMIT = 50


@dataclass(frozen=True)
class EmbeddingValidationContext:
    n_atom: int
    scf_method: str
    scf_driver: str


def nonempty_fragment_labels_from_list(labels: list[str]) -> list[str]:
    return [label for label in labels if str(label).strip()]


def validate_embedding_cross_fields(spec: EmbeddingSpec) -> None:
    if isinstance(spec, EmbeddingDmet):
        _validate_dmet_cross_fields(spec)
    elif isinstance(spec, EmbeddingPlugin):
        _validate_plugin_fields(spec)
    elif isinstance(spec, EmbeddingProjection):
        _validate_projection_cross_fields(spec)


def validate_embedding(spec: EmbeddingSpec, ctx: EmbeddingValidationContext) -> None:
    validate_embedding_cross_fields(spec)
    if isinstance(spec, EmbeddingDmet):
        _validate_dmet_context(spec, ctx)
    elif isinstance(spec, EmbeddingProjection):
        _validate_projection_atom_indices(spec, ctx.n_atom)
    if isinstance(spec, EmbeddingDmet) and (
        spec.dmet.hamiltonian_source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION
    ):
        _validate_schmidt_atom_indices_in_molecule(spec, ctx.n_atom)


def validate_embedding_backend_caps(
    spec: EmbeddingSpec,
    *,
    caps: SolverCapabilities,
    scf_driver: str,
) -> None:
    from qchem_stack.chem.pre_quantum_path import PreQuantumPath
    from qchem_stack.config.embedding_enums import EmbeddingMode
    from qchem_stack.config.embedding_helpers import is_projection_mulliken, is_schmidt_production

    driver = str(scf_driver).strip().lower()
    if driver == "precomputed":
        return
    if getattr(spec, "mode", None) == EmbeddingMode.PLUGIN:
        return
    if is_schmidt_production(spec):
        path = PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION
    elif is_projection_mulliken(spec):
        path = PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO
    else:
        path = PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK
    if path == PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION:
        if not caps.supports_schmidt_atomic_hamiltonian:
            raise ConfigurationError(
                "embedding.dmet.hamiltonian_source='schmidt_atomic_production' requires "
                f"backend Schmidt support (scf.driver={driver!r})."
            )
    elif (
        path == PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO
        and not caps.supports_projection_fragment_mulliken_hamiltonian
    ):
        raise ConfigurationError(
            "embedding.projection.quantum_hamiltonian='fragment_mulliken_mo' requires "
            f"backend projection support (scf.driver={driver!r})."
        )


def _validate_dmet_cross_fields(spec: EmbeddingDmet) -> None:
    dmet = spec.dmet
    source = dmet.hamiltonian_source
    if source == DmetHamiltonianSource.WHOLE_ACTIVE_SYSTEM:
        _validate_whole_active_system(spec)
    if source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION:
        _validate_schmidt_atomic_production(spec)
    if dmet.uniform_multifragment_toy and source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION:
        raise ValueError(
            "dmet.uniform_multifragment_toy cannot be combined with schmidt_atomic_production."
        )
    schmidt = dmet.schmidt
    if schmidt.run_mu_bisection and dmet.target_fragment_electrons is None:
        raise ValueError(
            "schmidt.run_mu_bisection requires embedding.dmet.target_fragment_electrons."
        )


def _validate_whole_active_system(spec: EmbeddingDmet) -> None:
    dmet = spec.dmet
    labels = nonempty_fragment_labels_from_list(dmet.fragment_labels)
    if dmet.multifragment_one_shot_shared_hamiltonian:
        if len(labels) < 2:
            raise ValueError(
                "embedding.dmet.multifragment_one_shot_shared_hamiltonian requires at least two "
                "non-empty embedding.dmet.fragment_labels entries."
            )
    elif len(labels) != 1:
        raise ValueError(
            "embedding.dmet.hamiltonian_source='whole_active_system' requires exactly one "
            "non-empty embedding.dmet.fragment_labels entry (unless "
            "multifragment_one_shot_shared_hamiltonian is True)."
        )


def _validate_schmidt_atomic_production(spec: EmbeddingDmet) -> None:
    schmidt = spec.dmet.schmidt
    if schmidt.multi_fragment_atom_groups:
        _validate_multi_fragment_groups(spec)
    elif not schmidt.fragment_atom_indices:
        raise ValueError(
            "schmidt_atomic_production requires non-empty embedding.dmet.schmidt.fragment_atom_indices "
            "when multi_fragment_atom_groups is empty."
        )


def _validate_multi_fragment_groups(spec: EmbeddingDmet) -> None:
    dmet = spec.dmet
    schmidt = dmet.schmidt
    if schmidt.fragment_atom_indices:
        raise ValueError(
            "Use either embedding.dmet.schmidt.fragment_atom_indices (single fragment) or "
            "multi_fragment_atom_groups, not both."
        )
    groups = schmidt.multi_fragment_atom_groups
    if any(not group for group in groups):
        raise ValueError("multi_fragment_atom_groups: each inner list must be non-empty")
    labels = nonempty_fragment_labels_from_list(dmet.fragment_labels)
    if labels and len(labels) != len(groups):
        raise ValueError(
            "When multi_fragment_atom_groups is set, embedding.dmet.fragment_labels "
            "must have the same length as groups (or be empty)."
        )
    if schmidt.multi_primary_fragment_index >= len(groups):
        raise ValueError("multi_primary_fragment_index is out of range for fragment groups")


def _validate_dmet_context(spec: EmbeddingDmet, ctx: EmbeddingValidationContext) -> None:
    if spec.dmet.hamiltonian_source != DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION:
        return
    if str(ctx.scf_method).strip().upper() != "RHF":
        raise ConfigurationError(
            "embedding.dmet.hamiltonian_source='schmidt_atomic_production' requires "
            "scf.method='RHF' (closed-shell single density matrix)."
        )
    cycles = int(spec.dmet.schmidt.dmet_max_cycles)
    if cycles < 1:
        raise ConfigurationError("embedding.dmet.schmidt.dmet_max_cycles must be at least 1.")
    if cycles > SCHMIDT_DMET_MAX_CYCLES_LIMIT:
        raise ConfigurationError(
            "embedding.dmet.schmidt.dmet_max_cycles exceeds limit "
            f"{SCHMIDT_DMET_MAX_CYCLES_LIMIT} (got {cycles})."
        )


def _validate_plugin_fields(spec: EmbeddingPlugin) -> None:
    plugin = spec.plugin
    if not (plugin.name or "").strip():
        raise ValueError("embedding.mode='plugin' requires embedding.plugin.name")
    if not (plugin.json_path or "").strip():
        raise ValueError("embedding.mode='plugin' requires embedding.plugin.json_path")


def _validate_projection_cross_fields(spec: EmbeddingProjection) -> None:
    proj = spec.projection
    if proj.quantum_hamiltonian != ProjectionQuantumHamiltonian.FRAGMENT_MULLIKEN_MO:
        return
    if not proj.fragment_atom_indices:
        raise ValueError(
            "embedding.projection.quantum_hamiltonian='fragment_mulliken_mo' requires non-empty "
            "embedding.projection.fragment_atom_indices."
        )


def _validate_projection_atom_indices(spec: EmbeddingProjection, n_atom: int) -> None:
    proj = spec.projection
    if proj.quantum_hamiltonian != ProjectionQuantumHamiltonian.FRAGMENT_MULLIKEN_MO:
        return
    for atom_index in proj.fragment_atom_indices:
        if atom_index < 0 or atom_index >= n_atom:
            raise ValueError(
                "embedding.projection.fragment_atom_indices: atom index "
                f"{atom_index} out of range (n_atom={n_atom})."
            )


def _validate_schmidt_atom_indices_in_molecule(spec: EmbeddingDmet, n_atom: int) -> None:
    schmidt = spec.dmet.schmidt
    indices: list[int] = []
    if schmidt.fragment_atom_indices:
        indices.extend(schmidt.fragment_atom_indices)
    for group in schmidt.multi_fragment_atom_groups:
        indices.extend(group)
    for atom_index in indices:
        if atom_index < 0 or atom_index >= n_atom:
            raise ValueError(
                f"embedding.dmet.schmidt atom index {atom_index} out of range (n_atom={n_atom})."
            )

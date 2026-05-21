"""Read-only helpers for nested :class:`~qchem_stack.config.embedding.EmbeddingSpec`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.exceptions import ConfigurationError

from .embedding_enums import DmetHamiltonianSource, ProjectionQuantumHamiltonian
from .embedding_specs import EmbeddingDmet, EmbeddingPlugin, EmbeddingProjection

if TYPE_CHECKING:
    from .embedding import EmbeddingSpec
    from .experiment import ExperimentConfig


def is_schmidt_production(spec: EmbeddingSpec) -> bool:
    return (
        isinstance(spec, EmbeddingDmet)
        and spec.dmet.hamiltonian_source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION
    )


def is_projection_mulliken(spec: EmbeddingSpec) -> bool:
    return (
        isinstance(spec, EmbeddingProjection)
        and spec.projection.quantum_hamiltonian == ProjectionQuantumHamiltonian.FRAGMENT_MULLIKEN_MO
    )


def nonempty_fragment_labels(spec: EmbeddingSpec) -> list[str]:
    if not isinstance(spec, EmbeddingDmet):
        return []
    return list(spec.dmet.fragment_labels)


def require_dmet(spec: EmbeddingSpec) -> EmbeddingDmet:
    if not isinstance(spec, EmbeddingDmet):
        raise ConfigurationError(
            f"Expected embedding.mode='dmet' (got {getattr(spec, 'mode', None)!r})."
        )
    return spec


def require_projection(spec: EmbeddingSpec) -> EmbeddingProjection:
    if not isinstance(spec, EmbeddingProjection):
        raise ConfigurationError(
            f"Expected embedding.mode='projection' (got {getattr(spec, 'mode', None)!r})."
        )
    return spec


def require_plugin(spec: EmbeddingSpec) -> EmbeddingPlugin:
    if not isinstance(spec, EmbeddingPlugin):
        raise ConfigurationError(
            f"Expected embedding.mode='plugin' (got {getattr(spec, 'mode', None)!r})."
        )
    return spec


def resolve_schmidt_per_fragment_vqe_maxiter(cfg: ExperimentConfig) -> int:
    spec = cfg.embedding
    if isinstance(spec, EmbeddingDmet):
        pf = spec.dmet.schmidt.per_fragment_vqe_maxiter
        if pf is not None:
            return int(pf)
    return int(cfg.quantum.vqe.maxiter)

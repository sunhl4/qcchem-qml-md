"""Pre-quantum branch enum and resolution — lives in config to avoid chem dependency."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from .embedding_enums import EmbeddingMode
from .embedding_helpers import is_projection_mulliken, is_schmidt_production

if TYPE_CHECKING:
    from .experiment import ExperimentConfig


class PreQuantumPath(str, Enum):
    """Stable branch id shared by validators, assembly, and ``hamiltonian_branch`` meta."""

    PRECOMPUTED_BUNDLE = "precomputed_bundle"
    EMBEDDING_PLUGIN = "embedding_plugin"
    SCHMIDT_ATOMIC_PRODUCTION = "schmidt_atomic_production"
    PROJECTION_FRAGMENT_MULLIKEN_MO = "projection_fragment_mulliken_mo"
    CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK = "canonical_active_space_integral_pack"


def resolve_pre_quantum_path(cfg: ExperimentConfig) -> PreQuantumPath:
    """Resolve which pre-quantum assembly path applies (live drivers only for precomputed)."""
    driver = str(cfg.scf.driver).strip().lower()
    if driver == "precomputed":
        return PreQuantumPath.PRECOMPUTED_BUNDLE
    emb = cfg.embedding
    if emb.mode == EmbeddingMode.PLUGIN:
        return PreQuantumPath.EMBEDDING_PLUGIN
    if is_schmidt_production(emb):
        return PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION
    if is_projection_mulliken(emb):
        return PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO
    return PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK


def list_pre_quantum_paths() -> tuple[PreQuantumPath, ...]:
    """Stable path order used by docs/tests/exporters."""
    return tuple(PreQuantumPath)


def list_pre_quantum_path_sources() -> tuple[str, ...]:
    """Stable list of ``PreQuantumInput.meta['source']`` values."""
    return tuple(path.value for path in list_pre_quantum_paths())


def pre_quantum_path_source(path: PreQuantumPath) -> str:
    """``PreQuantumInput.meta['source']`` string for a resolved path."""
    return path.value

"""Single source of truth for pre-quantum branch selection (config, build, parity)."""

from __future__ import annotations

from enum import Enum

from qchem_stack.config import ExperimentConfig


class PreQuantumPath(str, Enum):
    """Stable branch id shared by validators, assembly, and ``hamiltonian_branch`` meta."""

    PRECOMPUTED_BUNDLE = "precomputed_bundle"
    EMBEDDING_PLUGIN = "embedding_plugin"
    SCHMIDT_ATOMIC_PRODUCTION = "schmidt_atomic_production"
    PROJECTION_FRAGMENT_MULLIKEN_MO = "projection_fragment_mulliken_mo"
    CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK = "canonical_active_space_integral_pack"


def list_pre_quantum_paths() -> tuple[PreQuantumPath, ...]:
    """Stable path order used by docs/tests/exporters."""
    return tuple(PreQuantumPath)


def list_pre_quantum_path_sources() -> tuple[str, ...]:
    """Stable list of ``PreQuantumInput.meta['source']`` values."""
    return tuple(path.value for path in list_pre_quantum_paths())


def resolve_pre_quantum_path(cfg: ExperimentConfig) -> PreQuantumPath:
    """Resolve which pre-quantum assembly path applies (live drivers only for precomputed)."""
    driver = str(cfg.scf.driver).strip().lower()
    if driver == "precomputed":
        return PreQuantumPath.PRECOMPUTED_BUNDLE
    emb = cfg.embedding
    if emb.mode == "plugin":
        return PreQuantumPath.EMBEDDING_PLUGIN
    if emb.dmet_hamiltonian_source == "schmidt_atomic_production":
        return PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION
    if (
        emb.mode == "projection"
        and emb.projection_quantum_hamiltonian == "fragment_mulliken_mo"
    ):
        return PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO
    return PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK


def pre_quantum_path_source(path: PreQuantumPath) -> str:
    """``PreQuantumInput.meta['source']`` string for a resolved path."""
    return path.value

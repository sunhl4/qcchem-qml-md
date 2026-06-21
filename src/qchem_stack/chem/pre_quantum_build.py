"""Pre-quantum handoff assembly (chem layer; no orchestration imports)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.pre_quantum_branches import (
    branch_canonical_active_space_pack,
    branch_embedding_plugin,
    branch_precomputed_bundle,
    branch_projection_fragment_mulliken,
    branch_schmidt_atomic_production,
)
from qchem_stack.chem.pre_quantum_builder_registry import (
    PreQuantumBuildRequest,
    get_pre_quantum_branch_builder,
    register_pre_quantum_branch_builder,
)
from qchem_stack.chem.pre_quantum_path import PreQuantumPath, resolve_pre_quantum_path
from qchem_stack.chem.pre_quantum_schmidt import schmidt_hamiltonian_and_context
from qchem_stack.chem.solvers.registry import create_solver

__all__ = [
    "build_pre_quantum_input",
    "build_pre_quantum_input_with_context",
    "hamiltonian_with_schmidt_context",
    "schmidt_hamiltonian_and_context",
]

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.pre_quantum_input import PreQuantumInput
    from qchem_stack.config import ExperimentConfig


def build_pre_quantum_input_with_context(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
    cache=None,
    profile=None,
) -> tuple[PreQuantumInput, dict | None]:
    """Assemble :class:`PreQuantumInput` and optional Schmidt context for the sync pipeline."""
    _register_default_pre_quantum_branch_builders()
    path = resolve_pre_quantum_path(cfg)
    backend_caps = None
    if path in (
        PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION,
        PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO,
        PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK,
    ):
        backend_caps = create_solver(cfg).capabilities
    builder = get_pre_quantum_branch_builder(path)
    req = PreQuantumBuildRequest(
        cfg=cfg,
        reference=reference,
        cfg_path=cfg_path,
        cache=cache,
        profile=profile,
        backend_caps=backend_caps,
    )
    return builder(req)


def build_pre_quantum_input(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
    cache=None,
) -> PreQuantumInput:
    """Public chem entry: build :class:`PreQuantumInput` (same branches as the sync pipeline)."""
    pre_q, _ctx = build_pre_quantum_input_with_context(
        cfg, reference, cfg_path=cfg_path, cache=cache
    )
    return pre_q


# Backward-compatible alias used by orchestration and tests.
hamiltonian_with_schmidt_context = build_pre_quantum_input_with_context


_DEFAULT_BUILDERS_REGISTERED = False


def _register_default_pre_quantum_branch_builders() -> None:
    global _DEFAULT_BUILDERS_REGISTERED
    if _DEFAULT_BUILDERS_REGISTERED:
        return
    register_pre_quantum_branch_builder(
        PreQuantumPath.PRECOMPUTED_BUNDLE,
        branch_precomputed_bundle,
        allow_override=True,
    )
    register_pre_quantum_branch_builder(
        PreQuantumPath.EMBEDDING_PLUGIN,
        branch_embedding_plugin,
        allow_override=True,
    )
    register_pre_quantum_branch_builder(
        PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION,
        branch_schmidt_atomic_production,
        allow_override=True,
    )
    register_pre_quantum_branch_builder(
        PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO,
        branch_projection_fragment_mulliken,
        allow_override=True,
    )
    register_pre_quantum_branch_builder(
        PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK,
        branch_canonical_active_space_pack,
        allow_override=True,
    )
    _DEFAULT_BUILDERS_REGISTERED = True

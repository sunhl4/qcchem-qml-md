"""Pre-quantum branch builders registered against :class:`PreQuantumPath`."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.run_build_cache import pack_cache_key
from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    molecular_hamiltonian_from_canonical_active_space_pack,
)
from qchem_stack.chem.pre_quantum_input import PreQuantumInput, build_pre_quantum_meta
from qchem_stack.chem.pre_quantum_path import PreQuantumPath, pre_quantum_path_source
from qchem_stack.chem.pre_quantum_schmidt import schmidt_hamiltonian_and_context
from qchem_stack.chem.precomputed_pre_quantum import precomputed_pre_quantum_input
from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.exceptions import PipelineError

if TYPE_CHECKING:
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.bridges.run_build_cache import RunBuildCache
    from qchem_stack.chem.pre_quantum_builder_registry import PreQuantumBuildRequest
    from qchem_stack.chem.solvers.base import SolverCapabilities
    from qchem_stack.config import ExperimentConfig


def make_pre_quantum_input(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    qh: QubitHamiltonian,
    *,
    path: PreQuantumPath,
    pack: CanonicalActiveSpaceIntegralPack | None = None,
    meta_extra: dict[str, Any] | None = None,
) -> PreQuantumInput:
    source = pre_quantum_path_source(path)
    return PreQuantumInput(
        classical_reference=rhf,
        qubit_hamiltonian=qh,
        canonical_active_space_integral_pack=pack,
        meta=build_pre_quantum_meta(
            cfg,
            source=source,
            qubit_hamiltonian=qh,
            extra=meta_extra,
        ),
    )


def build_pre_quantum_from_embedding_plugin(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None,
) -> tuple[PreQuantumInput, None]:
    from qchem_stack.chem.embedding.decomposition_plugin import (
        qubit_hamiltonian_from_decomposition_plugin,
    )

    qh = qubit_hamiltonian_from_decomposition_plugin(cfg, cfg_path=cfg_path)
    qh_meta = dict(getattr(qh, "meta", {}) or {})
    return (
        make_pre_quantum_input(
            cfg,
            reference,
            qh,
            path=PreQuantumPath.EMBEDDING_PLUGIN,
            meta_extra={
                "decomposition_plugin": qh_meta.get("decomposition_plugin"),
                "decomposition_plugin_schema": qh_meta.get("decomposition_plugin_schema"),
            },
        ),
        None,
    )


def build_pre_quantum_from_projection_fragment_mulliken(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    backend_caps: SolverCapabilities | None = None,
) -> tuple[PreQuantumInput, None]:
    caps = backend_caps or create_solver(cfg).capabilities
    if not caps.supports_projection_fragment_mulliken_hamiltonian:
        raise PipelineError(
            "projection.fragment_mulliken_mo requires backend support "
            f"(backend={caps.backend_id!r})."
        )
    from qchem_stack.chem.embedding.projection_hamiltonian import (
        molecular_hamiltonian_fragment_mulliken_projection,
    )

    qh, _audit = molecular_hamiltonian_fragment_mulliken_projection(reference, cfg)
    return (
        make_pre_quantum_input(
            cfg,
            reference,
            qh,
            path=PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO,
        ),
        None,
    )


def build_pre_quantum_from_canonical_pack(
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cache: RunBuildCache | None,
    profile: Any | None,
    backend_caps: SolverCapabilities | None = None,
) -> tuple[PreQuantumInput, None]:
    caps = backend_caps or create_solver(cfg).capabilities
    if not caps.supports_restricted_active_space_qubit_hamiltonian:
        raise PipelineError(
            "This pipeline stage builds a qubit Hamiltonian from restricted active-space MO integrals; "
            f"the selected backend {caps.backend_id!r} does not provide "
            "a canonical active-space integral pack yet."
        )
    from qchem_stack.config.active_space_helpers import (
        resolve_fermion_qubit_mapping,
        resolve_n_electrons,
        resolve_n_orbitals,
    )

    active = cfg.active_space
    na = resolve_n_orbitals(active)
    ne = resolve_n_electrons(active)

    def _build_pack() -> CanonicalActiveSpaceIntegralPack:
        return CanonicalActiveSpaceIntegralPack.from_classical_reference(
            reference,
            n_active_orbitals=na,
            n_active_electrons=ne,
        )

    if cache is not None:
        key = pack_cache_key(cfg, reference, n_active_orbitals=na, n_active_electrons=ne)
        pack = cache.get_or_build_pack(key, _build_pack)
    else:
        pack = _build_pack()

    if profile is not None:
        profile.mark("canonical_pack_ms")
    from qchem_stack.chem.integration.crosscheck import maybe_attach_integral_crosscheck
    from qchem_stack.chem.integration.meta_schema import record_casci_active_integrals_binding

    record_casci_active_integrals_binding(reference.driver_meta, pack)
    maybe_attach_integral_crosscheck(cfg, reference, primary_pack=pack)
    qh = molecular_hamiltonian_from_canonical_active_space_pack(
        pack,
        n_active_orbitals=na,
        n_active_electrons=ne,
        fermion_qubit_mapping=resolve_fermion_qubit_mapping(active),
        prefer_restricted_spatial_fermion_for_jordan_wigner=active.jw.prefer_restricted_spatial,
        jordan_wigner_coeff_atol=active.jw.coeff_atol,
        classical_reference_for_meta=reference,
    )
    if profile is not None:
        profile.mark("fermion_to_qubit_ms")
    return (
        make_pre_quantum_input(
            cfg,
            reference,
            qh,
            path=PreQuantumPath.CANONICAL_ACTIVE_SPACE_INTEGRAL_PACK,
            pack=pack,
        ),
        None,
    )


def branch_precomputed_bundle(
    req: PreQuantumBuildRequest,
) -> tuple[PreQuantumInput, None]:
    return precomputed_pre_quantum_input(req.cfg, req.reference, cfg_path=req.cfg_path), None


def branch_embedding_plugin(
    req: PreQuantumBuildRequest,
) -> tuple[PreQuantumInput, None]:
    return build_pre_quantum_from_embedding_plugin(req.cfg, req.reference, cfg_path=req.cfg_path)


def branch_schmidt_atomic_production(
    req: PreQuantumBuildRequest,
) -> tuple[PreQuantumInput, dict[str, Any] | None]:
    qh, ctx = schmidt_hamiltonian_and_context(req.cfg, req.reference, backend_caps=req.backend_caps)
    return (
        make_pre_quantum_input(
            req.cfg,
            req.reference,
            qh,
            path=PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION,
        ),
        ctx,
    )


def branch_projection_fragment_mulliken(
    req: PreQuantumBuildRequest,
) -> tuple[PreQuantumInput, None]:
    return build_pre_quantum_from_projection_fragment_mulliken(
        req.cfg,
        req.reference,
        backend_caps=req.backend_caps,
    )


def branch_canonical_active_space_pack(
    req: PreQuantumBuildRequest,
) -> tuple[PreQuantumInput, None]:
    return build_pre_quantum_from_canonical_pack(
        req.cfg,
        req.reference,
        cache=req.cache,
        profile=req.profile,
        backend_caps=req.backend_caps,
    )

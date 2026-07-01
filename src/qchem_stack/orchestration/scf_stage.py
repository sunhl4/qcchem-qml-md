from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.exceptions import PipelineError

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.solvers.base import SolverCapabilities
    from qchem_stack.config import ExperimentConfig


def solver_capabilities(cfg: ExperimentConfig) -> SolverCapabilities:
    return create_solver(cfg).capabilities


def run_scf_reference(cfg: ExperimentConfig) -> ClassicalMeanFieldReference:
    from qchem_stack.chem.bridges.reference_factory import (
        classical_mean_field_reference_from_config,
    )

    return classical_mean_field_reference_from_config(cfg)


def refine_mean_field_for_active_space(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference
) -> ExperimentConfig:
    """AVAS projection (optional) + shared CASSCF kernel (audit/orbital feed)."""
    from qchem_stack.chem.active_space.backend_hooks import (
        casscf_orbital_pass,
        patch_experiment_active_space_resolution,
    )
    from qchem_stack.chem.active_space.mo_coeff_transform_hooks import apply_mo_coeff_transform_hook
    from qchem_stack.chem.kernels.dispatch import run_avas

    caps = solver_capabilities(cfg)
    if cfg.active_space.strategy == "avas":
        if not caps.supports_avas_active_space_projection:
            raise PipelineError(
                "active_space.strategy='avas' requires AVAS capability on the selected backend "
                f"(backend={caps.backend_id!r})."
            )
        run_avas(cfg, rhf)
        cfg = patch_experiment_active_space_resolution(cfg, rhf)

    audit = bool(cfg.chemistry_extended.casscf.orbital_optimization_audit)
    feed = bool(cfg.chemistry_extended.casscf.orbital_optimization_for_integrals)
    if audit or feed:
        if not caps.supports_casscf_orbital_audit:
            raise PipelineError(
                "casscf_orbital_* flags require CASSCF support on the selected backend "
                f"(backend={caps.backend_id!r})."
            )
        if cfg.chemistry_extended.pbc.cell_vectors_bohr is not None:
            raise PipelineError("CASSCF orbital hooks are unsupported on the PBC branch.")
        if cfg.scf.method != "RHF":
            raise PipelineError("casscf_orbital_* hooks require scf.method=RHF.")
        casscf_orbital_pass(
            cfg,
            rhf,
            update_integrals_orbitals=feed,
            record_audit=audit,
        )

    apply_mo_coeff_transform_hook(cfg, rhf)
    return cfg


def embedding_input_system_payload(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference
) -> dict[str, object] | None:
    rep = cfg.embedding.embedding_input_representation
    if rep == "mo":
        return None
    caps = solver_capabilities(cfg)
    if not caps.supports_embedding_input_ao_lowdin:
        raise PipelineError(
            "embedding_input_representation=ao/lowdin_orth_ao requires backend capability "
            f"'supports_embedding_input_ao_lowdin'; backend {caps.backend_id!r} lacks this capability."
        )
    if cfg.chemistry_extended.pbc.cell_vectors_bohr is not None:
        raise PipelineError(
            "embedding_input_representation=ao/lowdin_orth_ao is currently molecular-only (non-PBC)."
        )
    solver = create_solver(cfg)
    try:
        return solver.build_embedding_input_system(rhf, representation=rep)
    except NotImplementedError as exc:
        raise PipelineError(
            "embedding_input_representation export is not implemented for the selected backend "
            f"{solver.capabilities.backend_id!r}."
        ) from exc

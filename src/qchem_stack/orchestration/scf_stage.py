from __future__ import annotations

from typing import Any

from qchem_stack.chem.active_space.mean_field_meta import (
    apply_active_space_strategy_to_mean_field_meta,
)
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import PipelineError


def solver_capabilities(cfg: ExperimentConfig) -> Any:
    return create_solver(cfg).capabilities


def run_scf_reference(cfg: ExperimentConfig) -> ClassicalMeanFieldReference:
    from qchem_stack.chem.bridges import (
        classical_mean_field_via_solver_bridge,
        molecular_system_from_experiment,
    )

    if cfg.active_space.strategy == "manual":
        frz = list(cfg.active_space.frozen_orbitals)
        recipe = (
            "manual:"
            f"n_active_orbitals={cfg.active_space.n_active_orbitals},"
            f"n_active_electrons={cfg.active_space.n_active_electrons},"
            f"frozen_orbitals={frz}"
        )
    elif cfg.active_space.strategy == "avas_stub":
        recipe = (
            "avas_stub:"
            f"ncas={cfg.active_space.ncas},nelecas={cfg.active_space.nelecas}:partial_open_stack_no_avas_projection"
        )
    elif cfg.active_space.strategy == "avas":
        recipe = (
            "avas:"
            f"ao_labels={cfg.chemistry_extended.avas_ao_labels}:"
            f"threshold={cfg.chemistry_extended.avas_threshold}:pyscf_mcscf_avas"
        )
    else:
        recipe = f"cas:ncas={cfg.active_space.ncas},nelecas={cfg.active_space.nelecas}"
    mf_pack = classical_mean_field_via_solver_bridge(cfg)
    rhf = ClassicalMeanFieldReference.from_mean_field_pack(
        mf_pack,
        molecular_system=molecular_system_from_experiment(cfg),
    )
    apply_active_space_strategy_to_mean_field_meta(
        rhf.driver_meta,
        strategy=cfg.active_space.strategy,
        recipe=recipe,
        avas_ao_labels=cfg.chemistry_extended.avas_ao_labels,
    )
    if cfg.active_space.frozen_orbitals:
        rhf.driver_meta["active_space_frozen_orbitals"] = list(cfg.active_space.frozen_orbitals)
    return rhf


def refine_mean_field_for_active_space(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference
) -> ExperimentConfig:
    """AVAS projection (optional) + shared CASSCF kernel (audit/orbital feed)."""
    from qchem_stack.chem.active_space.mo_coeff_transform_hooks import apply_mo_coeff_transform_hook
    from qchem_stack.chem.active_space.pyscf_active_space_hooks import (
        apply_pyscf_avas_to_reference,
        casscf_energy_and_maybe_orbitals,
        patch_experiment_active_space_resolution,
    )

    caps = solver_capabilities(cfg)
    if cfg.active_space.strategy == "avas":
        if not caps.supports_avas_active_space_projection:
            raise PipelineError(
                "active_space.strategy='avas' requires AVAS capability on the selected backend "
                f"(backend={caps.backend_id!r})."
            )
        # PySCF plugin boundary: AVAS projection requires backend-native orbital projection hooks.
        apply_pyscf_avas_to_reference(cfg, rhf)
        cfg = patch_experiment_active_space_resolution(cfg, rhf)

    audit = bool(cfg.chemistry_extended.casscf_orbital_optimization_audit)
    feed = bool(cfg.chemistry_extended.casscf_orbital_optimization_for_integrals)
    if audit or feed:
        if not caps.supports_casscf_orbital_audit:
            raise PipelineError(
                "casscf_orbital_* flags require PySCF-style CASSCF support on the selected backend "
                f"(backend={caps.backend_id!r})."
            )
        if cfg.chemistry_extended.pbc_cell_vectors_bohr is not None:
            raise PipelineError("CASSCF orbital hooks are unsupported on the PBC branch.")
        if cfg.scf.method != "RHF":
            raise PipelineError("casscf_orbital_* hooks require scf.method=RHF.")
        casscf_energy_and_maybe_orbitals(
            cfg,
            rhf,
            update_integrals_orbitals=feed,
            record_audit=audit,
        )

    apply_mo_coeff_transform_hook(cfg, rhf)
    return cfg


def embedding_input_system_payload(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference
) -> dict[str, Any] | None:
    rep = cfg.embedding.embedding_input_representation
    if rep == "mo":
        return None
    caps = solver_capabilities(cfg)
    if not caps.supports_embedding_input_ao_lowdin:
        raise PipelineError(
            "embedding_input_representation=ao/lowdin_orth_ao requires backend capability "
            f"'supports_embedding_input_ao_lowdin'; backend {caps.backend_id!r} lacks this capability."
        )
    if cfg.chemistry_extended.pbc_cell_vectors_bohr is not None:
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

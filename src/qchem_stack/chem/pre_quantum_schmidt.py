"""Schmidt impurity Hamiltonian build (chem layer)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
    qubit_hamiltonian_from_spatial_chemist_integrals,
)
from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.config.active_space_helpers import resolve_fermion_qubit_mapping
from qchem_stack.config.embedding_helpers import nonempty_fragment_labels, require_dmet
from qchem_stack.contracts.schema_ids import SCHMIDT_PRODUCTION_PIPELINE_V1
from qchem_stack.exceptions import PipelineError

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def schmidt_hamiltonian_and_context(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    *,
    backend_caps: Any | None = None,
) -> tuple[QubitHamiltonian, dict[str, Any]]:
    """Build primary Schmidt impurity ``QubitHamiltonian`` and context."""
    caps = backend_caps or create_solver(cfg).capabilities
    if not caps.supports_schmidt_atomic_hamiltonian:
        raise PipelineError(
            "embedding.dmet.hamiltonian_source='schmidt_atomic_production' requires backend support "
            f"(backend={caps.backend_id!r})."
        )
    if rhf.backend_tag() not in ("pyscf", "psi4"):
        raise PipelineError(
            f"schmidt_atomic_production requires backend pyscf or psi4 (got {rhf.backend_tag()!r})."
        )
    if cfg.scf.method != "RHF":
        raise PipelineError(
            "embedding.dmet.hamiltonian_source='schmidt_atomic_production' requires scf.method='RHF' "
            "(closed-shell single density matrix)."
        )
    from qchem_stack.chem.embedding.schmidt_production import (
        apply_chemical_potential_fragment_block,
        bisection_mu_for_fragment_electron_count,
        fci_fragment_ground_state,
        fragment_mulliken_electrons,
    )
    from qchem_stack.integrations.schmidt_dmet_self_consistent import (
        run_schmidt_density_feedback_cycles,
        run_schmidt_multifragment_density_cycles,
    )

    emb = require_dmet(cfg.embedding)
    dmet = emb.dmet
    schmidt = dmet.schmidt
    groups = schmidt.multi_fragment_atom_groups
    if groups:
        labs = nonempty_fragment_labels(emb)
        model, dmet_loop_report, d_embed = run_schmidt_multifragment_density_cycles(
            rhf,
            fragment_atom_groups=[list(g) for g in groups],
            fragment_labels=labs if len(labs) == len(groups) else None,
            primary_fragment_index=int(schmidt.multi_primary_fragment_index),
            n_bath_orbitals=int(schmidt.n_bath_spatial),
            max_impurity_spatial_orbitals=int(schmidt.max_impurity_spatial_orbitals),
            max_cycles=int(schmidt.dmet_max_cycles),
            mixing_alpha=float(schmidt.dmet_mixing_alpha),
            convergence_tol=float(schmidt.dmet_convergence_tol),
        )
        multifrag_audit: dict[str, Any] = {
            "schmidt_multifragment": True,
            "n_embedding_fragments": len(groups),
            "primary_fragment_index": int(schmidt.multi_primary_fragment_index),
        }
        schmidt_ctx: dict[str, Any] = {
            "D_embed": d_embed,
            "fragment_groups": [list(g) for g in groups],
            "fragment_labels": list(dmet_loop_report.get("fragment_labels_used", [])),
        }
    else:
        model, dmet_loop_report, d_embed = run_schmidt_density_feedback_cycles(
            rhf,
            fragment_atom_indices=list(schmidt.fragment_atom_indices),
            n_bath_orbitals=int(schmidt.n_bath_spatial),
            max_impurity_spatial_orbitals=int(schmidt.max_impurity_spatial_orbitals),
            max_cycles=int(schmidt.dmet_max_cycles),
            mixing_alpha=float(schmidt.dmet_mixing_alpha),
            convergence_tol=float(schmidt.dmet_convergence_tol),
        )
        multifrag_audit = {}
        frag_labels = nonempty_fragment_labels(emb)
        schmidt_ctx = {
            "D_embed": d_embed,
            "fragment_groups": None,
            "fragment_labels": frag_labels if frag_labels else ["fragment_0"],
        }

    ao = rhf.ao_basis_view()
    s = ao.overlap_ao()
    frag_ao = list(model.meta.get("fragment_ao_indices", []))
    mulliken_frag = fragment_mulliken_electrons(d_embed, s, frag_ao)

    mu = 0.0
    mu_report: dict[str, Any] | None = None
    if schmidt.run_mu_bisection and dmet.target_fragment_electrons is not None:
        mu, mu_report = bisection_mu_for_fragment_electron_count(
            model,
            target_fragment_electrons=float(dmet.target_fragment_electrons),
        )

    h1_use = apply_chemical_potential_fragment_block(
        model.h1, mu=mu, n_fragment_spatial_orbitals=model.n_fragment_spatial_orbitals
    )
    ne = model.n_alpha_electrons + model.n_beta_electrons

    fci_ref: dict[str, Any] | None = None
    if mu_report is not None:
        if mu_report.get("status") == "converged" and isinstance(mu_report.get("fci_at_mu"), dict):
            fci_ref = mu_report["fci_at_mu"]  # type: ignore[assignment]
        elif mu_report.get("status") == "no_bracket" and isinstance(
            mu_report.get("fci_mu_zero"), dict
        ):
            fci_ref = mu_report["fci_mu_zero"]  # type: ignore[assignment]
    elif schmidt.attach_fci_reference and model.n_spatial_orbitals <= int(
        schmidt.fci_reference_max_spatial_orbitals
    ):
        fci_ref = fci_fragment_ground_state(model, mu=mu)

    audit: dict[str, Any] = {
        "schema": SCHMIDT_PRODUCTION_PIPELINE_V1,
        "impurity_model": dict(model.meta),
        "schmidt_dmet_self_consistency": dmet_loop_report,
        "mulliken_fragment_after_embedding_density": mulliken_frag,
        "mu_on_fragment_diagonal_au": float(mu),
        "mu_bisection_report": mu_report,
        "fci_impurity_reference": fci_ref,
        "impurity_n_spatial_orbitals": model.n_spatial_orbitals,
        "impurity_n_electrons": int(ne),
        "active_space_yaml_ignored_for_qh": True,
        "note": (
            "Main variational stage uses impurity qubit Hamiltonian "
            f"({resolve_fermion_qubit_mapping(cfg.active_space)!r}); cfg.active_space sizes apply to "
            "ledger/stub fields only on this path."
        ),
        **multifrag_audit,
    }
    qh = qubit_hamiltonian_from_spatial_chemist_integrals(
        model.constant,
        h1_use,
        model.h2,
        ne,
        fermion_qubit_mapping=resolve_fermion_qubit_mapping(cfg.active_space),
        integral_source="schmidt_impurity_spatial",
        meta_extra={"schmidt_production_audit": audit},
        classical_driver_meta=dict(rhf.driver_meta) if getattr(rhf, "driver_meta", None) else None,
        pyscf_driver_meta=dict(rhf.driver_meta)
        if getattr(rhf, "driver_meta", None) and rhf.backend_tag() == "pyscf"
        else None,
    )
    return qh, schmidt_ctx

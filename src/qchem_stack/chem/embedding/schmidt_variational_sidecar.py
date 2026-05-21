"""Optional per-fragment VQE on Schmidt impurities (post pre-quantum handoff, uses quantum layer)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_spatial_chemist_integrals
from qchem_stack.chem.pre_quantum_pyscf_gate import require_pyscf_reference
from qchem_stack.config.embedding_helpers import (
    require_dmet,
    resolve_schmidt_per_fragment_vqe_maxiter,
)
from qchem_stack.contracts.schema_ids import SCHMIDT_PER_FRAGMENT_VQE_V1
from qchem_stack.quantum.algorithms.vqe import VQE

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


def run_schmidt_per_fragment_vqe(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    schmidt_ctx: dict[str, Any],
    exe: Any,
) -> dict[str, Any] | None:
    """Independent VQE on each fragment impurity (post embedding density)."""
    groups = schmidt_ctx.get("fragment_groups")
    if not groups or len(groups) < 2:
        return None
    labels = schmidt_ctx.get("fragment_labels") or []
    if len(labels) != len(groups):
        return None
    if not require_dmet(cfg.embedding).dmet.schmidt.run_vqe_on_all_fragments:
        return None
    d = np.asarray(schmidt_ctx["D_embed"], dtype=float)
    dmet = require_dmet(cfg.embedding).dmet
    schmidt = dmet.schmidt
    from qchem_stack.chem.embedding.schmidt_production import build_schmidt_impurity_integrals

    mx = resolve_schmidt_per_fragment_vqe_maxiter(cfg)
    rows: list[dict[str, Any]] = []
    require_pyscf_reference(rhf, context="schmidt_run_vqe_on_all_fragments")
    for i, atoms in enumerate(groups):
        model = build_schmidt_impurity_integrals(
            rhf,
            fragment_atom_indices=list(atoms),
            n_bath_orbitals=int(schmidt.n_bath_spatial),
            max_impurity_spatial_orbitals=int(schmidt.max_impurity_spatial_orbitals),
            density_ao=d,
        )
        ne = model.n_alpha_electrons + model.n_beta_electrons
        qh_i = qubit_hamiltonian_from_spatial_chemist_integrals(
            model.constant,
            model.h1,
            model.h2,
            ne,
            fermion_qubit_mapping=cfg.active_space.mapping.fermion_qubit,
            integral_source="schmidt_impurity_spatial_fragment",
            meta_extra={"fragment_id": labels[i]},
        )
        vr = VQE(qh_i, depth=cfg.quantum.vqe.depth, executor=exe).run(
            maxiter=int(mx),
            seed=int(cfg.random_seed) + i * 31,
        )
        rows.append(
            {
                "fragment_id": labels[i],
                "atom_indices": list(atoms),
                "energy": float(vr.energy),
                "nfev": int(vr.nfev),
                "n_qubits": int(qh_i.n_qubits),
            }
        )
    return {
        "schema": SCHMIDT_PER_FRAGMENT_VQE_V1,
        "vqe_depth": cfg.quantum.vqe.depth,
        "vqe_maxiter_per_fragment": int(mx),
        "fragments": rows,
    }

"""DMET embedding workflow strategy."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from qchem_stack.chem.embedding.dmet import DMETContext
from qchem_stack.config.embedding_enums import DmetHamiltonianSource
from qchem_stack.config.embedding_helpers import nonempty_fragment_labels
from qchem_stack.config.quantum_helpers import resolve_vqe_depth, resolve_vqe_maxiter
from qchem_stack.contracts.schema_ids import ONIOM_TOY_V1
from qchem_stack.exceptions import PipelineError
from qchem_stack.integrations.dmet_self_consistent import (
    OneShotEmbeddingDriver,
    run_dmet_bath_scf_self_consistency_v1,
)
from qchem_stack.integrations.schmidt_per_fragment_vqe import run_schmidt_per_fragment_vqe

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.run_context import PipelineStageTimer

_log = logging.getLogger(__name__)


def run_dmet_fragment_solve_if_requested(
    cfg: ExperimentConfig,
    qh: QubitHamiltonian,
    exe: Any,
    out: dict[str, Any],
) -> None:
    """Optional impurity VQE on global active Hamiltonian (single-fragment DMET *shape* demo)."""
    from qchem_stack.config.embedding_enums import EmbeddingMode
    from qchem_stack.config.embedding_helpers import require_dmet

    if cfg.embedding.mode != EmbeddingMode.DMET:
        return
    emb = require_dmet(cfg.embedding)
    dmet = emb.dmet
    schmidt = dmet.schmidt
    if dmet.hamiltonian_source != DmetHamiltonianSource.WHOLE_ACTIVE_SYSTEM:
        return
    labels = nonempty_fragment_labels(emb)
    mf_shared = dmet.multifragment_one_shot_shared_hamiltonian
    if mf_shared:
        if len(labels) < 2:
            out["dmet_fragment_solve_error"] = (
                "expected at least two fragment labels for multifragment shared demo"
            )
            return
    elif len(labels) != 1:
        out["dmet_fragment_solve_error"] = "expected one fragment label (validator should catch)"
        return
    if dmet.fragment_solver.use_exact:
        from qchem_stack.chem.embedding.fragment_solvers.registry import resolve_fragment_solver

        solver = resolve_fragment_solver(
            dmet.fragment_solver.plugin_id,
            use_exact=True,
            exact_max_qubits=int(dmet.fragment_solver.exact_max_qubits),
        )
    else:
        from qchem_stack.chem.embedding.fragment_solvers.registry import resolve_fragment_solver

        solver = resolve_fragment_solver(
            dmet.fragment_solver.plugin_id,
            use_exact=False,
            executor=exe,
            vqe_depth=resolve_vqe_depth(cfg),
            vqe_maxiter=resolve_vqe_maxiter(cfg),
            random_seed=int(cfg.random_seed),
        )
    bath_n = (
        int(schmidt.n_bath_spatial)
        if dmet.hamiltonian_source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION
        else None
    )
    ctx = DMETContext(
        fragments=labels,
        solver=solver,
        n_scf_cycles_embedding=emb.n_scf_cycles_embedding,
        classical_reference_method=emb.classical_reference_method,
        bath_spatial_orbitals=bath_n,
    )
    frag_hams = {fid: qh for fid in labels} if mf_shared else {labels[0]: qh}
    ledger = OneShotEmbeddingDriver.run(ctx, frag_hams)
    ledger["hamiltonian_source"] = "whole_active_system"
    ledger["multifragment_shared_global_hamiltonian"] = bool(mf_shared)
    out["dmet_fragment_solve"] = ledger


class DmetStrategy:
    """Strategy for DMET embedding workflow."""

    def apply(
        self,
        cfg: ExperimentConfig,
        *,
        out: dict[str, Any],
        qh: QubitHamiltonian,
        exe: Any,
        embedding_input_payload: dict[str, Any] | None,
        schmidt_ctx: dict[str, Any] | None,
        rhf: ClassicalMeanFieldReference,
        cfg_path: Path | None,
        profile: PipelineStageTimer,
        emit: Callable[[str], None],
    ) -> None:
        from qchem_stack.config.embedding_specs import EmbeddingDmet

        if not isinstance(cfg.embedding, EmbeddingDmet):
            return

        emb = cfg.embedding
        dmet = emb.dmet
        schmidt = dmet.schmidt
        frag_labels = nonempty_fragment_labels(emb)
        wf = {
            "mode": "dmet",
            "fragment_count": len(frag_labels),
            "fragment_labels": frag_labels,
            "dmet_hamiltonian_source": dmet.hamiltonian_source,
            "fragment_solver_protocol": "qchem_stack.chem.embedding.dmet.FragmentSolverProtocol",
            "stage_timing": "post_variational",
        }
        if dmet.hamiltonian_source == DmetHamiltonianSource.WHOLE_ACTIVE_SYSTEM:
            wf["impurity_solver_used"] = (
                "qchem_stack.chem.embedding.dmet.QubitHamiltonianFragmentSolverExact"
                if dmet.fragment_solver.use_exact
                else "qchem_stack.integrations.dmet_fragment_solvers.QubitHamiltonianFragmentSolverVQE"
            )
            if dmet.multifragment_one_shot_shared_hamiltonian:
                wf["multifragment_one_shot_shared_hamiltonian"] = True
        elif dmet.hamiltonian_source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION:
            wf["impurity_hamiltonian"] = "qchem_stack.chem.embedding.schmidt_production"
            wf["main_variational_target"] = "impurity_qubit_hamiltonian_jw"
            wf["schmidt_dmet_max_cycles"] = int(schmidt.dmet_max_cycles)
            if schmidt.multi_fragment_atom_groups:
                wf["schmidt_multifragment_atom_groups"] = [
                    list(g) for g in schmidt.multi_fragment_atom_groups
                ]
                wf["schmidt_multi_primary_fragment_index"] = int(
                    schmidt.multi_primary_fragment_index
                )
                wf["schmidt_dmet_density_feedback_module"] = (
                    "qchem_stack.chem.embedding.schmidt_dmet_self_consistent."
                    "run_schmidt_multifragment_density_cycles"
                )
            else:
                wf["schmidt_fragment_atom_indices"] = list(schmidt.fragment_atom_indices)
                wf["schmidt_dmet_density_feedback_module"] = (
                    "qchem_stack.chem.embedding.schmidt_dmet_self_consistent."
                    "run_schmidt_density_feedback_cycles"
                )
        else:
            wf["solver_stub"] = "qchem_stack.chem.embedding.dmet.VQEFragmentSolverStub"
        bpath = (schmidt.bath_sidecar_json_path or "").strip()
        if bpath:
            if dmet.hamiltonian_source != DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION:
                raise PipelineError(
                    "embedding.dmet.schmidt.bath_sidecar_json_path requires "
                    "dmet.hamiltonian_source=='schmidt_atomic_production'"
                )
            side_path = Path(bpath)
            if not side_path.is_file() and cfg_path is not None:
                side_path = (cfg_path.parent / bpath).resolve()
            if not side_path.is_file():
                raise PipelineError(
                    f"schmidt.bath_sidecar_json_path not found: {bpath!r} (resolved {side_path})"
                )
            wf["schmidt_bath_sidecar_v1"] = json.loads(side_path.read_text(encoding="utf-8"))
        if cfg.embedding.oniom_layers_v1:
            wf["oniom_toy_v1"] = {
                "schema": ONIOM_TOY_V1,
                "layers": [dict(x) for x in cfg.embedding.oniom_layers_v1],
            }
        if embedding_input_payload is not None:
            wf["embedding_input_system"] = embedding_input_payload
        out["embedding_workflow"] = wf
        n_cycles = emb.n_scf_cycles_embedding
        if (
            n_cycles is not None
            and int(n_cycles) >= 2
            and dmet.hamiltonian_source == DmetHamiltonianSource.WHOLE_ACTIVE_SYSTEM
        ):
            labs_sc = nonempty_fragment_labels(emb)
            rep = run_dmet_bath_scf_self_consistency_v1(
                cfg,
                labs_sc,
                qh,
                exe,
                max_cycles=int(n_cycles),
            )
            out["dmet_self_consistency_loop"] = rep
            wf["dmet_self_consistency_loop_v1"] = {
                "schema": rep.get("schema"),
                "converged": rep.get("converged"),
                "cycles": rep.get("cycles"),
            }
        run_dmet_fragment_solve_if_requested(cfg, qh, exe, out)
        if schmidt_ctx is not None:
            spfv = run_schmidt_per_fragment_vqe(cfg, rhf, schmidt_ctx, exe)
            if spfv is not None:
                out["schmidt_per_fragment_vqe"] = spfv
                _log.info(
                    "pipeline schmidt_per_fragment_vqe_done experiment_id=%s n_fragments=%s",
                    cfg.experiment_id,
                    len(spfv.get("fragments") or []),
                )
        if dmet.uniform_multifragment_toy:
            labs_mc = nonempty_fragment_labels(emb)
            if len(labs_mc) >= 2:
                from qchem_stack.integrations.dmet_multifragment_toy import (
                    run_uniform_hamiltonian_multifragment_toy,
                )

                out["dmet_uniform_multifragment_toy"] = run_uniform_hamiltonian_multifragment_toy(
                    cfg, labs_mc, qh, exe, max_cycles=1
                )
        profile.mark("embedding_dmet")
        emit("embedding_dmet")

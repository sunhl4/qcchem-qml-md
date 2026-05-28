"""Embedding workflow strategy pattern implementations."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from qchem_stack.chem.embedding.dmet import (
    DMETContext,
    QubitHamiltonianFragmentSolverExact,
)
from qchem_stack.config.embedding_enums import (
    DmetHamiltonianSource,
    ProjectionQuantumHamiltonian,
)
from qchem_stack.config.embedding_helpers import nonempty_fragment_labels
from qchem_stack.config.quantum_helpers import resolve_vqe_depth, resolve_vqe_maxiter
from qchem_stack.contracts.schema_ids import (
    EMBEDDING_WORKFLOW_V1,
    ONIOM_TOY_V1,
    PROJECTION_EMBEDDING_WORKFLOW_V1,
)
from qchem_stack.exceptions import PipelineError
from qchem_stack.integrations.dmet_fragment_solvers import QubitHamiltonianFragmentSolverVQE
from qchem_stack.integrations.dmet_self_consistent import OneShotEmbeddingDriver
from qchem_stack.integrations.schmidt_per_fragment_vqe import run_schmidt_per_fragment_vqe

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.run_context import PipelineStageTimer

_log = logging.getLogger(__name__)


@runtime_checkable
class EmbeddingStrategy(Protocol):
    """Protocol for embedding workflow strategies."""

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
        """Apply the embedding workflow strategy."""
        ...


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
        solver: Any = QubitHamiltonianFragmentSolverExact(
            max_qubits=int(dmet.fragment_solver.exact_max_qubits)
        )
    else:
        solver = QubitHamiltonianFragmentSolverVQE(
            depth=resolve_vqe_depth(cfg),
            maxiter=resolve_vqe_maxiter(cfg),
            executor=exe,
            random_seed=cfg.random_seed,
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


class ProjectionStrategy:
    """Strategy for projection embedding workflow."""

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
        from qchem_stack.config.embedding_specs import EmbeddingProjection

        if not isinstance(cfg.embedding, EmbeddingProjection):
            return

        proj = cfg.embedding.projection
        wf = {
            "mode": "projection",
            "schema": PROJECTION_EMBEDDING_WORKFLOW_V1,
            "projection_low_level": proj.low_level,
            "projection_high_level": proj.high_level,
            "projection_threshold": float(proj.threshold),
            "projection_quantum_hamiltonian": proj.quantum_hamiltonian,
            "parity_module": "qchem_stack.chem.embedding.projection",
            "stage_timing": "post_variational",
        }
        hm = out.get("hamiltonian_meta") or {}
        audit = hm.get("projection_mulliken_mo_audit_v1")
        if audit:
            wf["projection_selected_mo_indices"] = list(audit.get("selected_mo_indices") or [])
            wf["projection_mulliken_weights"] = list(audit.get("mulliken_weights") or [])
            wf["projection_integral_source"] = audit.get("integral_source")
        if proj.quantum_hamiltonian == ProjectionQuantumHamiltonian.FRAGMENT_MULLIKEN_MO:
            wf["caveat"] = (
                "Main-line VQE uses fragment Mulliken-selected active integrals "
                "(qchem_stack.chem.embedding.projection_hamiltonian)."
            )
            wf["epistemic_bound"] = "Fragment-local MO screening; not full projection embedding."
        else:
            wf["caveat"] = (
                "Quantum stage uses global active-space JW Hamiltonian; this branch records projection trace metadata."
            )
            wf["epistemic_bound"] = (
                "Open reproducibility — not closed-source projection driver parity."
            )
        if embedding_input_payload is not None:
            wf["embedding_input_system"] = embedding_input_payload
        out["embedding_workflow"] = wf
        profile.mark("embedding_projection")
        emit("embedding_projection")


class PluginStrategy:
    """Strategy for plugin embedding workflow."""

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
        from qchem_stack.config.embedding_specs import EmbeddingPlugin

        if not isinstance(cfg.embedding, EmbeddingPlugin):
            return

        plugin = cfg.embedding.plugin
        hm = out.get("hamiltonian_meta") or {}
        resolved_json = hm.get("decomposition_plugin_json")
        term_counts = hm.get("decomposition_fragment_pauli_term_counts")
        term_total = 0
        if isinstance(term_counts, dict):
            term_total = sum(int(v) for v in term_counts.values())
        out["embedding_workflow"] = {
            "schema": EMBEDDING_WORKFLOW_V1,
            "mode": "plugin",
            "decomposition_plugin": plugin.name,
            "decomposition_plugin_json_path": plugin.json_path,
            "decomposition_plugin_json_resolved_path": resolved_json,
            "decomposition_primary_fragment_id": hm.get("decomposition_primary_fragment_id"),
            "decomposition_fragment_count": hm.get("decomposition_fragment_count"),
            "decomposition_fragment_ids": hm.get("decomposition_fragment_ids"),
            "decomposition_fragment_pauli_term_counts": term_counts,
            "decomposition_total_pauli_terms": term_total,
            "decomposition_plugin_schema": hm.get("decomposition_plugin_schema"),
            "decomposition_fragment_energy_terms_v1": hm.get(
                "decomposition_fragment_energy_terms_v1"
            ),
            "stage_timing": "post_variational",
            "integral_source": hm.get("integral_source"),
            "epistemic_bound": (
                "Open decomposition-plugin contract v1 (optional per-fragment energy-term stubs) "
                "— not closed-source embedding/decomposition product parity."
                if hm.get("decomposition_plugin_schema") == "decomposition_plugin_contract_v1"
                else (
                    "Open plugin boundary (toy v1 JSON) — not closed decomposition product parity."
                )
            ),
            "note": "Toy decomposition-plugin Hamiltonian replaces molecular active-space build.",
        }
        if embedding_input_payload is not None:
            out["embedding_workflow"]["embedding_input_system"] = embedding_input_payload
        profile.mark("embedding_plugin")
        emit("embedding_plugin")


class NoneStrategy:
    """Strategy for no embedding workflow."""

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
        from typing import cast

        out["embedding_workflow"] = {
            "schema": EMBEDDING_WORKFLOW_V1,
            "mode": "none",
            "stage_timing": "post_variational",
            "note": "No DMET/projection embedding stage; variational Hamiltonian uses global active space.",
        }
        if embedding_input_payload is not None:
            cast("dict[str, Any]", out["embedding_workflow"])["embedding_input_system"] = (
                embedding_input_payload
            )
        profile.mark("embedding_none")
        emit("embedding_none")

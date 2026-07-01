"""Projection embedding workflow strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.config.embedding_enums import ProjectionQuantumHamiltonian
from qchem_stack.contracts.schema_ids import PROJECTION_EMBEDDING_WORKFLOW_V1

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.run_context import PipelineStageTimer


class ProjectionStrategy:
    """Strategy for projection embedding workflow."""

    def apply(
        self,
        cfg: ExperimentConfig,
        *,
        out: dict[str, object],
        qh: QubitHamiltonian,
        exe: object,
        embedding_input_payload: dict[str, object] | None,
        schmidt_ctx: dict[str, object] | None,
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
        raw_hm = out.get("hamiltonian_meta")
        hm: dict[str, object] = raw_hm if isinstance(raw_hm, dict) else {}
        audit_raw = hm.get("projection_mulliken_mo_audit_v1")
        audit = audit_raw if isinstance(audit_raw, dict) else {}
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

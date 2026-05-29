"""Plugin embedding workflow strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import EMBEDDING_WORKFLOW_V1

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.orchestration.run_context import PipelineStageTimer


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

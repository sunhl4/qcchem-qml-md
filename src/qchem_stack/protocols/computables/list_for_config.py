"""Config-driven computable listing."""

from __future__ import annotations

from qchem_stack.config import ExperimentConfig
from qchem_stack.config.quantum_helpers import (
    classify_pauli_expectation_path_for_config,
    excited_qse_after_variational,
    excited_sceom_after_variational,
    excited_vqd_after_variational,
    pauli_protocol_enabled,
    qpe_demo_track_requested,
    quantum_workflow_preview_vqs_fields,
    resolve_adapt_max_iter,
    resolve_excited_qse_subspace_dim,
    resolve_excited_sceom_subspace_dim,
    resolve_excited_vqd_n_states,
    resolve_iqeb_max_rounds,
    resolve_pauli_grouping,
    resolve_quantum_algorithm_factory,
    resolve_variational_algorithm,
    resolve_variational_ansatz,
    resolve_vqe_depth,
    vqs_track_requested,
)
from qchem_stack.protocols.computables.graph_v2 import refs_from_computable_graph_v2
from qchem_stack.protocols.computables.refs import ComputableRef, ComputableSpec


def list_computables_for_config(cfg: ExperimentConfig) -> list[ComputableRef]:
    """List what the current YAML is configured to *evaluate* (best-effort, documentation-first)."""
    out: list[ComputableRef] = []
    algo = resolve_variational_algorithm(cfg)
    if resolve_quantum_algorithm_factory(cfg):
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {
                    "algorithm_label": algo,
                    "variational_dispatch": "yaml_algorithm_factory_v1",
                    "algorithm_factory": resolve_quantum_algorithm_factory(cfg),
                    "vqe_depth": resolve_vqe_depth(cfg),
                },
            )
        )
    elif algo == "vqe":
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {"algorithm": "vqe", "vqe_depth": resolve_vqe_depth(cfg)},
            )
        )
    elif algo in ("adapt", "tetris_adapt"):
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {"algorithm": algo, "adapt_max_iter": resolve_adapt_max_iter(cfg)},
            )
        )
    elif algo == "iqeb":
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {
                    "algorithm": "iqeb",
                    "iqeb_max_rounds": resolve_iqeb_max_rounds(cfg),
                    "vqe_depth": resolve_vqe_depth(cfg),
                },
            )
        )
    else:
        out.append(
            ComputableRef(
                "ground_state_energy",
                "energy",
                {
                    "algorithm": algo,
                    "variational_plugin_registry_id": algo,
                    "vqe_depth": resolve_vqe_depth(cfg),
                },
            )
        )
    if pauli_protocol_enabled(cfg):
        out.append(
            ComputableRef(
                "hamiltonian_expectation_pauli_protocol",
                "energy",
                {
                    "pauli_grouping": resolve_pauli_grouping(cfg),
                    "pauli_protocol_expectation_path": classify_pauli_expectation_path_for_config(
                        cfg
                    ),
                },
            )
        )
    if excited_vqd_after_variational(cfg):
        out.append(
            ComputableRef(
                "excited_energies_vqd",
                "spectrum",
                {"n_states": resolve_excited_vqd_n_states(cfg)},
            )
        )
    if excited_qse_after_variational(cfg):
        qse_details: dict[str, object] = {"subspace_dim": resolve_excited_qse_subspace_dim(cfg)}
        if resolve_variational_ansatz(cfg) == "uccsd":
            qse_details.update(
                {
                    "shot_mode": cfg.quantum.excited.qse.shot_mode,
                    "expansion_pool": cfg.quantum.excited.qse.expansion_pool,
                }
            )
            out.append(
                ComputableRef(
                    "qse_matrices_uccsd",
                    "spectrum",
                    qse_details,
                )
            )
        out.append(
            ComputableRef(
                "excitation_energies_qse",
                "spectrum",
                qse_details,
            )
        )
    if excited_sceom_after_variational(cfg):
        out.append(
            ComputableRef(
                "sceom_energies",
                "spectrum",
                {"subspace_dim": resolve_excited_sceom_subspace_dim(cfg)},
            )
        )
    if qpe_demo_track_requested(cfg):
        out.append(
            ComputableRef(
                "qpe_demo_track", "phase", {"hook": "qpe_qec_demo.kitaev + bayesian_stub"}
            )
        )
    if vqs_track_requested(cfg):
        vqs_fields = quantum_workflow_preview_vqs_fields(cfg)
        out.append(
            ComputableRef(
                "vqs_track",
                "dynamics",
                {
                    "hook": "quantum.algorithms.vqs + vqs_pipeline_track",
                    "vqs_mode": vqs_fields["vqs_mode"],
                    "vqs_n_times": vqs_fields["vqs_n_times"],
                },
            )
        )
    return out


def list_computable_specs_for_config(cfg: ExperimentConfig) -> list[ComputableSpec]:
    return [ComputableSpec.from_ref(r) for r in list_computables_for_config(cfg)]


def assert_computable_workflow_graph_roundtrip(cfg: ExperimentConfig) -> None:
    """``computable_graph_v2`` ↔ :func:`refs_from_computable_graph_v2` matches :func:`list_computables_for_config`.

    L1 / wave-F: guarantees workflow-preview DAG nodes round-trip to the same ref list (order + payloads).

    Raises:
        ValueError: If roundtrip validation fails (length mismatch or content mismatch).
    """
    from qchem_stack.protocols.workflow_preview import computable_graph_v2

    refs = list_computables_for_config(cfg)
    graph = computable_graph_v2(refs, cfg)
    back = refs_from_computable_graph_v2(graph)

    if len(back) != len(refs):
        raise ValueError(
            f"Computable workflow graph roundtrip failed: length mismatch (refs={len(refs)}, back={len(back)})"
        )

    for a, b in zip(refs, back, strict=True):
        if a.name != b.name or a.kind != b.kind or a.details != b.details:
            raise ValueError(
                f"Computable workflow graph roundtrip failed: content mismatch (ref={a}, back={b})"
            )


def computables_export_dict(
    cfg: ExperimentConfig,
    protocol_counts: dict[str, object] | None = None,
) -> dict[str, object]:
    """JSON-friendly blob for :mod:`scripts.export_parity_criteria_table`.

    When ``protocol_counts`` is passed (e.g. from a finished pipeline run), marks that the
    Pauli support set is available for strict :func:`~qchem_stack.protocols.pauli_support.assert_evaluate_compatible` checks.
    """
    support_from = bool(
        protocol_counts is not None and protocol_counts.get("hamiltonian_pauli_strings") is not None
    )
    return {
        "schema": "qchem_computable_abstract_v2",
        "pauli_protocol_expectation_path": classify_pauli_expectation_path_for_config(cfg),
        "evaluate_note": (
            "Strict evaluate reuse (conservative): each required Pauli label must appear "
            "in hamiltonian_pauli_strings from protocol_counts; see "
            "qchem_stack.protocols.pauli_support.assert_evaluate_compatible."
        ),
        "support_set_exported_from_protocol": support_from,
        "items": [
            {"name": c.name, "kind": c.kind, "details": c.details}
            for c in list_computables_for_config(cfg)
        ],
    }

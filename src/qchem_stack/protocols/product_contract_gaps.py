"""Product capability gaps and documentation-facing capability maps."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from qchem_stack.contracts.schema_ids import (
    PRODUCT_CAPABILITY_SLA_V1,
    PRODUCT_GAP_ANCHOR_INDEX_V1,
)

# Normalized SLA labels for docs / release surfaces.
_SLA_STATUS_NORMALIZE: dict[str, str] = {
    "available": "available",
    "partial": "partial",
    "partial_runtime": "partial",
    "stub_only": "stub_only",
    "n/a": "n/a",
    "local_runtime_only": "local_runtime_only",
    "reference": "partial",
}

_REPO_ROOT = Path(__file__).resolve().parents[3]

PRODUCT_CAPABILITY_MAP: dict[str, str] = {
    "ProtocolLifecycle": "qchem_stack.protocols.protocol.PauliAveragingProtocol + ProtocolPhase",
    "VQE": "qchem_stack.quantum.algorithms.vqe.VQE",
    "AdaptVQE": "qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE",
    "IQEB": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE",
    "ExcitedStateVQDQSE": "qchem_stack.quantum.algorithms.excited",
    "SCEOM": "qchem_stack.quantum.algorithms.sceom.run_sceom_nested_commutator_from_hea",
    "QPETracks": "qchem_stack.quantum.algorithms.qpe + qchem_stack.qpe_qec_demo.pipeline_track",
    "VQSTracks": "qchem_stack.quantum.algorithms.vqs + vqs_pipeline_track",
    "ComputableGraph": "qchem_stack.protocols.computable + workflow_preview.computable_graph_v2 integration",
    "ResourceRows": "qchem_stack.backends.spec.circuit_resource_row + dataframe_circuit_shot_rows",
    "JobRuntime": "qchem_stack.jobs.store.SqliteJobStore + qchem_stack.jobs.nexus_analog",
    "MitigationPipeline": "qchem_stack.mitigation.qermit_analog + qchem_stack.mitigation.qermit_runtime",
    "ChemistryDrivers": "qchem_stack.chem.solvers + qchem_stack.chem.bridges (legacy: chem.drivers)",
    "EmbeddingFlow": "qchem_stack.chem.embedding + qchem_stack.chem.embedding.dmet_self_consistent",
    "MLMDBridge": "qchem_stack.md_bridge",
}

PRODUCT_GAP_CATEGORIES_V1: list[dict[str, Any]] = [
    {
        "id": "managed_cloud_runtime",
        "release_anchor": "product_capability_matrix.md#managed-cloud-runtime",
        "open_stack_surface": "Local SQLite queue, optional HTTP sidecar adapters, and analog billing only.",
        "status": "local_runtime_only",
    },
    {
        "id": "http_submission_workspace_ops",
        "release_anchor": "product_capability_matrix.md#http-submission-and-ops",
        "open_stack_surface": "FastAPI submit/list/poll endpoints with project/workspace fields.",
        "status": "available",
    },
    {
        "id": "mitigation_batch_scheduler",
        "release_anchor": "product_capability_matrix.md#mitigation-runtime",
        "open_stack_surface": (
            "DAG + linear trace with PMSV/ZNE (Richardson + circuit fold), SPAM 2-qubit calibration, "
            "and classical-shadows main-path computable; local async mitigation job queue only "
            "(not Nexus MitRes/MitEx)."
        ),
        "status": "partial_runtime",
    },
    {
        "id": "computable_composition_surface",
        "release_anchor": "product_capability_matrix.md#computable-and-workflow-preview",
        "open_stack_surface": "Computable graph preview and rich slices are implemented for YAML-driven flows.",
        "status": "available",
    },
    {
        "id": "evaluate_support_set_reasoning",
        "release_anchor": "product_capability_matrix.md#evaluate-support-set",
        "open_stack_surface": "Conservative Pauli set-containment checks are implemented.",
        "status": "available",
    },
    {
        "id": "compiler_pass_depth",
        "release_anchor": "product_capability_matrix.md#compiler-and-pass-bundle",
        "open_stack_surface": (
            "CompilerSpec + CircuitIR pass bundle with routing/decompose/optimize presets; "
            "optional pytket CI probe; vendor ion routing passes remain n/a."
        ),
        "status": "available",
    },
    {
        "id": "chemically_aware_ansatz_pack",
        "release_anchor": "product_capability_matrix.md#ansatz-and-operator-pools",
        "open_stack_surface": (
            "HEA, UCCSD, UCCGD, QCC, UpCCGSD, pUCCD, VSQS; iterative iQCC/iQCC+PT "
            "(open-stack) and QITE research plugin; JW/BK/SCBK/JKMN/HCB mapping paths."
        ),
        "status": "available",
    },
    {
        "id": "operator_pool_taxonomy_depth",
        "release_anchor": "product_capability_matrix.md#operator-pool-registry",
        "open_stack_surface": (
            "Executable ADAPT/IQEB pools including staggered singles/doubles, BK slices, "
            "generalized doubles, and IQEB qubit-excitation aliases; not vendor full taxonomy."
        ),
        "status": "available",
        "evidence": [
            "configs/example_h2_adapt_staggered_pool.yaml",
            "configs/example_h2_adapt_bk_pool.yaml",
            "configs/example_h2_adapt_generalized_doubles_pool.yaml",
            "configs/example_h2_iqeb_bk_singles_pool.yaml",
        ],
    },
    {
        "id": "dmet_self_consistency_depth",
        "release_anchor": "product_capability_matrix.md#embedding-and-dmet",
        "open_stack_surface": (
            "PySCF density-feedback bath loop v1, Schmidt sidecar, projection workflows, "
            "ONIOM/QM-MM production demos; full cuTensorNet-scale DMET remains out of scope."
        ),
        "status": "available",
        "evidence": [
            "configs/example_h4_dmet_self_consistent.yaml",
            "configs/example_h2_dimer_dmet_self_consistent.yaml",
            "configs/example_h4_dmet_fragment_exact_small.yaml",
            "configs/example_h2_uniform_multifragment_toy.yaml",
        ],
    },
    {
        "id": "tensor_network_engine",
        "release_anchor": "product_capability_matrix.md#tensor-network",
        "open_stack_surface": "Stub workflow and strategy resolution are available; full production contraction stack is out of scope.",
        "status": "stub_only",
    },
    {
        "id": "integration_closure",
        "release_anchor": "product_capability_matrix.md#integration-closure-layer",
        "open_stack_surface": "Integration closure helpers are available as open reference implementations.",
        "status": "reference",
    },
    {
        "id": "uccsd_scbk_trotter_circuit",
        "release_anchor": "docs/技术文档_UCCSD_JW与BK_SCBK电路边界.md",
        "open_stack_surface": (
            "UCCSD product-formula Trotter circuits are supported for JW and BK only; "
            "SCBK UCCSD Trotter remains n/a (HEA+SCBK and mapping registry document the boundary)."
        ),
        "status": "n/a",
    },
    {
        "id": "driver_surface_breadth",
        "release_anchor": "product_capability_matrix.md#driver-surface",
        "open_stack_surface": (
            "PySCF and Psi4 via ChemIntegralSolver registry; mock external solver demo; "
            "ORCA/Gaussian intentionally out of scope (see docs/product/non_goals.md)."
        ),
        "status": "partial",
    },
    {
        "id": "device_shot_histogram_flow",
        "release_anchor": "product_capability_matrix.md#shot-histogram-paths",
        "open_stack_surface": "Statevector grouped shots and Qiskit counts pipelines are implemented.",
        "status": "available",
    },
]


def product_capability_map_for_docs() -> dict[str, str]:
    """Product-facing capability map."""
    return dict(PRODUCT_CAPABILITY_MAP)


def product_gap_categories() -> list[dict[str, Any]]:
    """Product-facing capability gaps for release surfaces."""
    return [dict(row) for row in PRODUCT_GAP_CATEGORIES_V1]


def normalize_capability_sla_status(status: str) -> str:
    """Map a gap ``status`` string to an SLA label.

    Allowed labels: ``available``, ``partial``, ``stub_only``, ``n/a``,
    ``local_runtime_only``. Unknown statuses become ``n/a``.
    """
    key = str(status).strip().lower()
    return _SLA_STATUS_NORMALIZE.get(key, "n/a")


def product_capability_sla_v1() -> dict[str, Any]:
    """Map each :data:`PRODUCT_GAP_CATEGORIES_V1` row to a normalized SLA label."""
    rows: list[dict[str, Any]] = []
    by_id: dict[str, str] = {}
    for gap in PRODUCT_GAP_CATEGORIES_V1:
        rid = str(gap["id"])
        raw_status = str(gap.get("status", "n/a"))
        sla = normalize_capability_sla_status(raw_status)
        by_id[rid] = sla
        rows.append(
            {
                "id": rid,
                "release_anchor": gap.get("release_anchor"),
                "status": raw_status,
                "sla": sla,
                "open_stack_surface": gap.get("open_stack_surface"),
            }
        )
    return {
        "schema": PRODUCT_CAPABILITY_SLA_V1,
        "by_id": by_id,
        "rows": rows,
    }


def _gap_id_and_anchor_pairs(gaps: list[dict[str, Any]]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for row in gaps:
        rid = row.get("id")
        anchor = row.get("release_anchor")
        if isinstance(rid, str) and rid and isinstance(anchor, str) and anchor:
            pairs.append((rid, anchor))
    return pairs


def product_gap_anchor_index_v1() -> dict[str, Any]:
    """Stable index for gap ``id`` <-> ``release_anchor`` mappings."""
    gaps = product_gap_categories()
    pairs = _gap_id_and_anchor_pairs(gaps)
    return {
        "schema": PRODUCT_GAP_ANCHOR_INDEX_V1,
        "id_to_anchor": {rid: anchor for rid, anchor in pairs},
        "anchor_to_ids": {
            anchor: sorted([rid for rid, anchor2 in pairs if anchor2 == anchor])
            for anchor in sorted({anchor for _, anchor in pairs})
        },
    }


def validate_product_gap_categories() -> list[str]:
    """Validate row-level invariants for :func:`product_gap_categories`."""
    gaps = product_gap_categories()
    errors: list[str] = []
    if not isinstance(gaps, list) or not gaps:
        return ["gaps must be a non-empty list"]
    ids: list[str] = []
    anchors: list[str] = []
    for idx, row in enumerate(gaps):
        if not isinstance(row, dict):
            errors.append(f"row[{idx}] must be mapping")
            continue
        rid = row.get("id")
        if not isinstance(rid, str) or not rid:
            errors.append(f"row[{idx}] missing non-empty id")
        else:
            ids.append(rid)
        anchor = row.get("release_anchor")
        if not isinstance(anchor, str) or not anchor:
            errors.append(f"row[{idx}] missing non-empty release_anchor")
        else:
            anchors.append(anchor)
        evidence = row.get("evidence")
        if evidence is not None:
            if not isinstance(evidence, list):
                errors.append(f"row[{idx}] evidence must be a list when present")
            else:
                rid_label = rid if isinstance(rid, str) and rid else f"row[{idx}]"
                for path in evidence:
                    if not isinstance(path, str) or not path:
                        errors.append(f"{rid_label}: evidence entries must be non-empty strings")
                        continue
                    if not (_REPO_ROOT / path).is_file():
                        errors.append(f"{rid_label}: missing evidence file {path}")
    if len(ids) != len(set(ids)):
        errors.append("duplicated gap id detected")
    if len(anchors) != len(set(anchors)):
        errors.append("duplicated release_anchor detected")
    return errors

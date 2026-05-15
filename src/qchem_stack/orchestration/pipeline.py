from __future__ import annotations

import hashlib
import json
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.backends.spec import summarize_circuit_shot_rows
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.embedding.dmet import (
    DMETContext,
    QubitHamiltonianFragmentSolverExact,
    QubitHamiltonianFragmentSolverVQE,
)
from qchem_stack.chem.hamiltonian import (
    QubitHamiltonian,
)
from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.config import (
    ExperimentConfig,
    backend_spec_from_config,
    compiler_pass_bundle_from_config,
    load_experiment_config,
)
from qchem_stack.exceptions import PipelineError
from qchem_stack.integrations.dmet_self_consistent import OneShotEmbeddingDriver
from qchem_stack.jobs.nexus_analog import nexus_analog_ledger_from_rows
from qchem_stack.jobs.nexus_cloud import nexus_cloud_repro_sidecar
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.mitigation.pmsv import PMSVConfig
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.mitigation.qermit_runtime import execute_mitigation_dag_runtime
from qchem_stack.orchestration.parity_finalize import (
    finalize_open_stack_parity_snapshot as _finalize_open_stack_parity_snapshot_impl,
)
from qchem_stack.orchestration.parity_finalize import (
    schmidt_per_fragment_vqe_parity_summary as _schmidt_per_fragment_vqe_parity_summary_impl,
)
from qchem_stack.orchestration.pre_quantum_stage import (
    hamiltonian as _hamiltonian_impl,
)
from qchem_stack.orchestration.pre_quantum_stage import (
    hamiltonian_with_schmidt_context as _hamiltonian_with_schmidt_context_impl,
)
from qchem_stack.orchestration.pre_quantum_stage import (
    require_pyscf_reference as _require_pyscf_reference_impl,
)
from qchem_stack.orchestration.pre_quantum_stage import (
    run_schmidt_per_fragment_vqe as _run_schmidt_per_fragment_vqe_impl,
)
from qchem_stack.orchestration.precomputed_stage import (
    is_precomputed_driver,
    normalize_precomputed_bundle_path,
    precomputed_pre_quantum_input,
)
from qchem_stack.orchestration.repro_metadata import (
    collect_repro_metadata_impl as _collect_repro_metadata_impl,
)
from qchem_stack.orchestration.repro_snapshot import (
    append_open_stack_parity_fields as _append_open_stack_parity_fields_impl,
)
from qchem_stack.orchestration.repro_snapshot import (
    repro_quantum_snapshot as _repro_quantum_snapshot_impl,
)
from qchem_stack.orchestration.repro_summary import (
    attach_run_summary as _attach_run_summary_impl,
)
from qchem_stack.orchestration.repro_summary import (
    classical_benchmark_summary as _classical_benchmark_summary_impl,
)
from qchem_stack.orchestration.run_context import PipelineStageTimer, RunContext
from qchem_stack.orchestration.scf_stage import (
    embedding_input_system_payload,
    refine_mean_field_for_active_space,
    run_scf_reference,
    solver_capabilities,
)
from qchem_stack.orchestration.stage_execution import (
    PreQuantumStageContext,
    ScfStageContext,
    build_pre_quantum_stage,
    run_scf_stage,
)
from qchem_stack.protocols.protocol import PauliAveragingProtocol
from qchem_stack.quantum.algorithms.excited import QSE, VQD
from qchem_stack.quantum.variational_plugins.registry import run_variational_stage
from qchem_stack.quantum.variational_plugins.spec import VariationalRunContext

_pipeline_log = logging.getLogger(__name__)


def _repro_quantum_snapshot(cfg: ExperimentConfig, qh: QubitHamiltonian | None) -> dict[str, Any]:
    return _repro_quantum_snapshot_impl(cfg, qh)


def _append_open_stack_parity_fields(snap: dict[str, Any], cfg: ExperimentConfig) -> None:
    _append_open_stack_parity_fields_impl(snap, cfg)


def _schmidt_per_fragment_vqe_parity_summary(spfv: dict[str, Any]) -> dict[str, Any]:
    return _schmidt_per_fragment_vqe_parity_summary_impl(spfv)


def _finalize_open_stack_parity_snapshot(
    out: dict[str, Any],
    cfg: ExperimentConfig,
    proto: PauliAveragingProtocol | None,
) -> None:
    _finalize_open_stack_parity_snapshot_impl(out, cfg, proto)


def _run_dmet_fragment_solve_if_requested(
    cfg: ExperimentConfig,
    qh: QubitHamiltonian,
    exe: Any,
    out: dict[str, Any],
) -> None:
    """Optional impurity VQE on global active Hamiltonian (single-fragment DMET *shape* demo)."""
    if cfg.embedding.mode != "dmet":
        return
    if cfg.embedding.dmet_hamiltonian_source != "whole_active_system":
        return
    emb = cfg.embedding
    labels = [x for x in emb.fragment_labels if str(x).strip()]
    mf_shared = emb.dmet_multifragment_one_shot_shared_hamiltonian
    if mf_shared:
        if len(labels) < 2:
            out["dmet_fragment_solve_error"] = (
                "expected at least two fragment labels for multifragment shared demo"
            )
            return
    elif len(labels) != 1:
        out["dmet_fragment_solve_error"] = "expected one fragment label (validator should catch)"
        return
    if emb.dmet_fragment_use_exact_solver:
        solver: Any = QubitHamiltonianFragmentSolverExact(
            max_qubits=int(emb.dmet_fragment_exact_max_qubits)
        )
    else:
        solver = QubitHamiltonianFragmentSolverVQE(
            depth=cfg.quantum.vqe_depth,
            maxiter=cfg.quantum.vqe_maxiter,
            executor=exe,
            random_seed=cfg.random_seed,
        )
    bath_n = (
        int(emb.schmidt_n_bath_spatial)
        if emb.dmet_hamiltonian_source == "schmidt_atomic_production"
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


def collect_repro_metadata(
    cfg: ExperimentConfig,
    cfg_path: Path | None = None,
    qh: QubitHamiltonian | None = None,
) -> dict[str, Any]:
    return _collect_repro_metadata_impl(
        cfg,
        parity_snapshot_fn=_repro_quantum_snapshot,
        cfg_path=cfg_path,
        qh=qh,
    )


def _require_pyscf_reference(
    rhf: ClassicalMeanFieldReference,
    *,
    context: str,
) -> Any:
    return _require_pyscf_reference_impl(rhf, context=context)


def _is_precomputed_driver(cfg: ExperimentConfig) -> bool:
    return is_precomputed_driver(cfg)


def _normalize_precomputed_bundle_path(
    cfg: ExperimentConfig, *, cfg_path: Path | None
) -> ExperimentConfig:
    return normalize_precomputed_bundle_path(cfg, cfg_path=cfg_path)


def _precomputed_pre_quantum_input(
    cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference, *, cfg_path: Path | None
) -> PreQuantumInput:
    return precomputed_pre_quantum_input(cfg, rhf, cfg_path=cfg_path)


def _run_schmidt_per_fragment_vqe(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    schmidt_ctx: dict[str, Any],
    exe: Any,
) -> dict[str, Any] | None:
    return _run_schmidt_per_fragment_vqe_impl(cfg, rhf, schmidt_ctx, exe)


def _hamiltonian_with_schmidt_context(
    cfg: ExperimentConfig,
    rhf: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
) -> tuple[PreQuantumInput, dict[str, Any] | None]:
    return _hamiltonian_with_schmidt_context_impl(
        cfg,
        rhf,
        cfg_path=cfg_path,
    )


def _hamiltonian(cfg: ExperimentConfig, rhf: ClassicalMeanFieldReference) -> QubitHamiltonian:
    return _hamiltonian_impl(cfg, rhf)


def _excited_protocol_contract_v1_block() -> dict[str, Any]:
    """Stable documentation slice for parity / Methods (shot semantics mirror YAML + implementation)."""

    return {
        "schema": "excited_protocol_contract_v1",
        "vqd_three_protocol": (
            "`objective`: deflation energy channel (exact statevector expectation or grouped Pauli when "
            "`vqd_shots_objective`>0). `overlap`: swap-test overlaps between solved levels when "
            "`vqd_shots_overlap`>0. `weight`: reserved coupling to overlap shot budget."
        ),
        "qse_shot_modes": {
            "exact": (
                "Dense Hamiltonian projected into QSE basis built from HEA single-reference determinants/"
                "excitations."
            ),
            "gaussian_h": (
                "`qse_shots_per_matrix_element` injects symmetric Gaussian noise on real parts of dense "
                "matrix elements — placeholder shot model vs device POVM."
            ),
            "pauli_transitions": (
                "Per-(i,j) transition channel built from Pauli transition strings; budgets via "
                "`qse_shots_per_ij_term` × schedule task count (`qse_total_shots_upper_bound`)."
            ),
        },
        "sceom_shot_semantics": (
            "When `sceom_shots_per_matrix_element`>0, apply symmetric Gaussian noise to real diagonal/"
            "off-diagonal entries of the nested-commutator matrix before GHEP (open-stack SCEOM prototype)."
        ),
    }


def build_excited_resource_summary_for_export(cfg: ExperimentConfig) -> dict[str, Any] | None:
    """VQD / QSE / SCEOM shot book-keeping from YAML only (for ``export_parity_criteria_table`` without a run)."""
    q = cfg.quantum
    if not (q.vqd_after_variational or q.qse_after_variational or q.sceom_after_variational):
        return None
    er: dict[str, Any] = {}
    if q.vqd_after_variational:
        ns = q.vqd_n_states
        n_exc = max(0, ns - 1)
        n_pairs = n_exc * (n_exc + 1) // 2
        er["vqd"] = {
            "n_states": ns,
            "shots_objective_per_reporting_level": q.vqd_shots_objective,
            "shots_overlap_per_pair": q.vqd_shots_overlap,
            "shots_weight_channel": q.vqd_shots_weight,
            "deflated_cobyla_levels": n_exc,
            "swap_test_pair_count_if_shots": n_pairs if q.vqd_shots_overlap > 0 else 0,
        }
    if q.qse_after_variational:
        er["qse"] = {
            "shot_mode": q.qse_shot_mode,
            "qse_shots_per_matrix_element_yaml": q.qse_shots_per_matrix_element,
            "qse_shots_per_ij_term_yaml": q.qse_shots_per_ij_term,
        }
    if q.sceom_after_variational:
        k = q.sceom_subspace_dim
        er["sceom"] = {
            "generator_count_k": k,
            "m_matrix_elements": k * k,
            "shots_per_matrix_element_yaml": q.sceom_shots_per_matrix_element,
        }
    ch = _excited_shot_channel_upper_bounds(er)
    er["shot_channel_upper_bounds"] = ch
    er["excited_methods_unified"] = _excited_methods_unified(er)
    er["excited_protocol_contract_v1"] = _excited_protocol_contract_v1_block()
    return er


def _build_excited_resource_summary(
    cfg: ExperimentConfig,
    out: dict[str, Any],
) -> dict[str, Any] | None:
    """YAML + run meta for Methods-style shot/task accounting (VQD / QSE / SCEOM stages)."""
    q = cfg.quantum
    if not (q.vqd_after_variational or q.qse_after_variational or q.sceom_after_variational):
        return None
    er: dict[str, Any] = {}
    if q.vqd_after_variational:
        ns = q.vqd_n_states
        n_exc = max(0, ns - 1)
        n_pairs = n_exc * (n_exc + 1) // 2
        er["vqd"] = {
            "n_states": ns,
            "shots_objective_per_reporting_level": q.vqd_shots_objective,
            "shots_overlap_per_pair": q.vqd_shots_overlap,
            "shots_weight_channel": q.vqd_shots_weight,
            "deflated_cobyla_levels": n_exc,
            "swap_test_pair_count_if_shots": n_pairs if q.vqd_shots_overlap > 0 else 0,
        }
    if q.qse_after_variational and "qse" in out:
        meta = out["qse"].get("meta") or {}
        block: dict[str, Any] = {"shot_mode": q.qse_shot_mode, "K": meta.get("K")}
        sched = meta.get("qse_pauli_transition_schedule")
        if isinstance(sched, dict):
            block["n_transition_tasks"] = sched.get("n_transition_tasks")
            block["total_shots_upper_bound"] = sched.get("total_shots_upper_bound")
            block["n_pauli_terms_in_schedule"] = sched.get("n_pauli_terms")
        if q.qse_shot_mode == "gaussian_h":
            k = meta.get("K")
            if isinstance(k, int) and k > 0:
                block["h_matrix_elements"] = k * k
                block["gaussian_h_shots_budget_reference"] = k * k * q.qse_shots_per_matrix_element
        if q.qse_shot_mode == "pauli_transitions":
            block["shots_per_ij_term_yaml"] = q.qse_shots_per_ij_term
        er["qse"] = {k2: v for k2, v in block.items() if v is not None}
    if q.sceom_after_variational:
        k = q.sceom_subspace_dim
        er["sceom"] = {
            "generator_count_k": k,
            "m_matrix_elements": k * k,
            "shots_per_matrix_element_yaml": q.sceom_shots_per_matrix_element,
        }
    ch = _excited_shot_channel_upper_bounds(er)
    er["shot_channel_upper_bounds"] = ch
    er["excited_methods_unified"] = _excited_methods_unified(er)
    er["excited_protocol_contract_v1"] = _excited_protocol_contract_v1_block()
    return er


def _vqd_channel_upper(v: dict[str, Any]) -> int:
    n = 0
    pairs = int(v.get("swap_test_pair_count_if_shots") or 0)
    sov = int(v.get("shots_overlap_per_pair") or 0)
    n += pairs * sov
    levels = int(v.get("deflated_cobyla_levels") or 0)
    obj = int(v.get("shots_objective_per_reporting_level") or 0)
    n += levels * obj
    sw = int(v.get("shots_weight_channel") or 0)
    if sw > 0 and sov > 0:
        n += levels * sw
    return n


def _qse_channel_upper(qs: dict[str, Any]) -> int:
    tub = qs.get("total_shots_upper_bound")
    if isinstance(tub, (int, float)) and tub > 0:
        return int(tub)
    gref = qs.get("gaussian_h_shots_budget_reference")
    if isinstance(gref, (int, float)) and gref > 0:
        return int(gref)
    nt = qs.get("n_transition_tasks")
    sp = qs.get("shots_per_ij_term_yaml")
    if (
        isinstance(nt, (int, float))
        and isinstance(sp, (int, float))
        and int(nt) > 0
        and int(sp) > 0
    ):
        return int(nt) * int(sp)
    return 0


def _sceom_channel_upper(sc: dict[str, Any]) -> int:
    m = int(sc.get("m_matrix_elements") or 0)
    sp = int(sc.get("shots_per_matrix_element_yaml") or 0)
    if m > 0 and sp > 0:
        return m * sp
    return 0


def _excited_shot_channel_upper_bounds(excited: dict[str, Any]) -> dict[str, int]:
    """Per-channel upper bounds (VQD / QSE / SCEOM) for Methods one-table accounting."""
    out: dict[str, int] = {"vqd": 0, "qse": 0, "sceom": 0, "combined": 0}
    v = excited.get("vqd")
    if isinstance(v, dict):
        out["vqd"] = _vqd_channel_upper(v)
    qs = excited.get("qse")
    if isinstance(qs, dict):
        out["qse"] = _qse_channel_upper(qs)
    sc = excited.get("sceom")
    if isinstance(sc, dict):
        out["sceom"] = _sceom_channel_upper(sc)
    out["combined"] = int(out["vqd"] + out["qse"] + out["sceom"])
    return out


def _excited_shots_upper_bound(excited: dict[str, Any]) -> int:
    """Conservative additive upper bound on shot-like budgets declared for excited stages (YAML + QSE schedule)."""
    b = _excited_shot_channel_upper_bounds(excited)
    return int(b["combined"])


def _excited_methods_unified(excited_rs: dict[str, Any]) -> dict[str, Any]:
    """Single export shape for VQD / QSE / SCEOM (Methods one-block)."""
    return {
        "schema_version": "1",
        "vqd": excited_rs.get("vqd"),
        "qse": excited_rs.get("qse"),
        "sceom": excited_rs.get("sceom"),
        "shot_channel_upper_bounds": excited_rs.get("shot_channel_upper_bounds"),
    }


def _attach_nexus_mitigation_tn(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Nexus / HQC analog, Qermit-style mitigation graph report, optional CuTensorNet stub."""
    if cfg.nexus_analog.enabled:
        rows = out.get("resource_rows")
        if rows is None:
            rows = out.get("pauli_measurement_ledger")
        led = nexus_analog_ledger_from_rows(list(rows or []), cfg)
        if led is not None:
            out["nexus_analog_ledger"] = led
    mgr = build_qermit_style_mitigation_report(cfg)
    if mgr is not None:
        out["mitigation_graph_report"] = mgr
    dex = execute_mitigation_dag_runtime(cfg, out)
    if dex is not None:
        out["mitigation_dag_execution"] = dex
    nc = nexus_cloud_repro_sidecar(cfg)
    if nc is not None:
        out["nexus_cloud_repro"] = nc
    if cfg.quantum.tensornet_expectation_stub:
        from qchem_stack.tensornet import run_cutensornet_expectation_stub

        out["tensornet_protocol_stub"] = run_cutensornet_expectation_stub(
            qh.n_qubits, requested_backend=cfg.quantum.tensornet_contraction_engine
        )


def _attach_qpe_demo_track_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Optional dense QPE + Bayesian toy, same as ``scripts/run_qpe_track_demo.py`` (NISQ + FT narrative)."""
    if not cfg.quantum.qpe_demo_track_requested():
        return
    from qchem_stack.qpe_qec_demo.pipeline_track import qpe_demo_track_payload

    out["qpe_demo_track"] = qpe_demo_track_payload(qh, bits=int(cfg.quantum.qpe_demo_track_n_bits))


def _attach_vqs_track_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Optional VQS / McLachlan dynamics on variational parameters (YAML ``vqs_rhs_mode`` for McLachlan modes)."""
    if not cfg.quantum.vqs_track_requested():
        return
    ang = out.get("angles")
    if ang is None:
        return
    from qchem_stack.quantum.algorithms.vqs_pipeline_track import vqs_track_payload

    q = cfg.quantum
    out["vqs_track"] = vqs_track_payload(
        qh,
        ang,
        mode=q.vqs_mode,
        n_times=q.vqs_n_times,
        dt=float(q.vqs_dt),
        rhs_mode_yaml=q.vqs_rhs_mode,
        tangent_fd_epsilon_yaml=float(q.vqs_tangent_fd_epsilon),
    )


def _attach_qpe_three_algorithm_pack_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Dense QPE trio from :mod:`~qchem_stack.quantum.algorithms.qpe` (config ``qpe_three_pack_*``)."""
    if not cfg.quantum.qpe_three_pack_requested():
        return
    from qchem_stack.quantum.algorithms.qpe import (
        AlgorithmDeterministicQPE,
        AlgorithmInfoTheoryQPE,
        AlgorithmKitaevQPE,
    )

    qt = cfg.quantum
    t_ev = float(qt.qpe_three_pack_time)

    def _row(public: str, res: Any) -> dict[str, Any]:
        meta = getattr(res, "meta", None)
        md = dict(meta) if isinstance(meta, dict) else {}
        return {
            "algorithm": public,
            "phase_mu": float(getattr(res, "phase_mu", 0.0)),
            "phase_sigma": float(getattr(res, "phase_sigma", 0.0)),
            "energy_estimate": float(getattr(res, "energy_estimate", float("nan"))),
            "meta": md,
        }

    det = AlgorithmDeterministicQPE(
        qh, time=t_ev, n_rounds=int(qt.qpe_three_pack_deterministic_rounds)
    )
    kit = AlgorithmKitaevQPE(qh, time=t_ev, n_bits=int(qt.qpe_three_pack_kitaev_bits))
    inf = AlgorithmInfoTheoryQPE(qh, time=t_ev, n_samples=int(qt.qpe_three_pack_info_samples))

    rd = det.build().run()
    rk = kit.build().run()
    ri = inf.build().run(seed=int(cfg.random_seed))

    out["qpe_algorithm_three_pack"] = {
        "schema": "qpe_algorithm_three_pack_v1",
        "time": float(t_ev),
        "yaml_note": (
            "Dense-spectrum emulation on the Hamiltonian Hilbert space; phase summaries are illustrative."
        ),
        "deterministic_qpe_report_v1": _row("deterministic_qpe", rd),
        "kitaev_qpe_report_v1": _row("kitaev_qpe", rk),
        "info_theory_qpe_report_v1": _row("info_theory_qpe", ri),
        "yaml_flags": {
            "qpe_three_pack_after_variational": bool(qt.qpe_three_pack_after_variational)
        },
        "implementations": {
            "deterministic": "qchem_stack.quantum.algorithms.qpe.AlgorithmDeterministicQPE",
            "kitaev": "qchem_stack.quantum.algorithms.qpe.AlgorithmKitaevQPE",
            "info_theory": "qchem_stack.quantum.algorithms.qpe.AlgorithmInfoTheoryQPE",
        },
    }


def _resource_summary_excited_only(n_qubits: int, excited_rs: dict[str, Any]) -> dict[str, Any]:
    ub = _excited_shots_upper_bound(excited_rs)
    rs: dict[str, Any] = {
        "n_circuits": 0,
        "sum_shots": 0,
        "max_depth": 0,
        "sum_twoq": 0,
        "n_qubits": n_qubits,
        "n_pauli_terms": None,
        "n_pauli_groups": None,
        "pauli_averaging_protocol_ran": False,
        "excited_stages": excited_rs,
        "excited_shots_upper_bound": ub,
        "sum_shots_total_with_excited_upper_bound": ub,
    }
    if isinstance(excited_rs.get("shot_channel_upper_bounds"), dict):
        rs["excited_shot_accounting"] = excited_rs["shot_channel_upper_bounds"]
    rs["excited_methods_unified"] = _excited_methods_unified(excited_rs)
    return rs


def _maybe_attach_md_ml_qmef_dataset(
    out: dict[str, Any],
    cfg: ExperimentConfig,
    reference: ClassicalMeanFieldReference,
    *,
    cfg_path: Path | None = None,
) -> None:
    """Optional ``repro.qmef_ml_attachment_v1`` for MD→ML export (see :mod:`qchem_stack.md_bridge`)."""
    if not cfg.md_ml_export.attach_single_frame_to_repro:
        return
    repro = out.get("repro")
    if not isinstance(repro, dict):
        return
    from qchem_stack.md_bridge.from_pipeline import build_qmef_ml_attachment_repro_block

    repro["qmef_ml_attachment_v1"] = build_qmef_ml_attachment_repro_block(
        cfg, out, reference, cfg_path=cfg_path
    )


def _apply_embedding_workflow_stage(
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
    if cfg.embedding.mode == "dmet":
        wf: dict[str, Any] = {
            "mode": "dmet",
            "fragment_count": len(cfg.embedding.fragment_labels),
            "fragment_labels": list(cfg.embedding.fragment_labels),
            "dmet_hamiltonian_source": cfg.embedding.dmet_hamiltonian_source,
            "fragment_solver_protocol": "qchem_stack.chem.embedding.dmet.FragmentSolverProtocol",
        }
        if cfg.embedding.dmet_hamiltonian_source == "whole_active_system":
            wf["impurity_solver_used"] = (
                "qchem_stack.chem.embedding.dmet.QubitHamiltonianFragmentSolverExact"
                if cfg.embedding.dmet_fragment_use_exact_solver
                else "qchem_stack.chem.embedding.dmet.QubitHamiltonianFragmentSolverVQE"
            )
            if cfg.embedding.dmet_multifragment_one_shot_shared_hamiltonian:
                wf["multifragment_one_shot_shared_hamiltonian"] = True
        elif cfg.embedding.dmet_hamiltonian_source == "schmidt_atomic_production":
            wf["impurity_hamiltonian"] = "qchem_stack.chem.embedding.schmidt_production"
            wf["main_variational_target"] = "impurity_qubit_hamiltonian_jw"
            wf["schmidt_dmet_max_cycles"] = int(cfg.embedding.schmidt_dmet_max_cycles)
            if cfg.embedding.schmidt_multi_fragment_atom_groups:
                wf["schmidt_multifragment_atom_groups"] = [
                    list(g) for g in cfg.embedding.schmidt_multi_fragment_atom_groups
                ]
                wf["schmidt_multi_primary_fragment_index"] = int(
                    cfg.embedding.schmidt_multi_primary_fragment_index
                )
                wf["schmidt_dmet_density_feedback_module"] = (
                    "qchem_stack.integrations.schmidt_dmet_self_consistent."
                    "run_schmidt_multifragment_density_cycles"
                )
            else:
                wf["schmidt_fragment_atom_indices"] = list(
                    cfg.embedding.schmidt_fragment_atom_indices
                )
                wf["schmidt_dmet_density_feedback_module"] = (
                    "qchem_stack.integrations.schmidt_dmet_self_consistent.run_schmidt_density_feedback_cycles"
                )
        else:
            wf["solver_stub"] = "qchem_stack.chem.embedding.dmet.VQEFragmentSolverStub"
        bpath = (cfg.embedding.schmidt_bath_sidecar_json_path or "").strip()
        if bpath:
            if cfg.embedding.dmet_hamiltonian_source != "schmidt_atomic_production":
                raise PipelineError(
                    "embedding.schmidt_bath_sidecar_json_path requires "
                    "dmet_hamiltonian_source=='schmidt_atomic_production'"
                )
            side_path = Path(bpath)
            if not side_path.is_file() and cfg_path is not None:
                side_path = (cfg_path.parent / bpath).resolve()
            if not side_path.is_file():
                raise PipelineError(
                    f"schmidt_bath_sidecar_json_path not found: {bpath!r} (resolved {side_path})"
                )
            wf["schmidt_bath_sidecar_v1"] = json.loads(side_path.read_text(encoding="utf-8"))
        if cfg.embedding.oniom_layers_v1:
            wf["oniom_toy_v1"] = {
                "schema": "oniom_toy_v1",
                "layers": [dict(x) for x in cfg.embedding.oniom_layers_v1],
            }
        if embedding_input_payload is not None:
            wf["embedding_input_system"] = embedding_input_payload
        out["embedding_workflow"] = wf
        _run_dmet_fragment_solve_if_requested(cfg, qh, exe, out)
        if schmidt_ctx is not None:
            spfv = _run_schmidt_per_fragment_vqe(cfg, rhf, schmidt_ctx, exe)
            if spfv is not None:
                out["schmidt_per_fragment_vqe"] = spfv
                _pipeline_log.info(
                    "pipeline schmidt_per_fragment_vqe_done experiment_id=%s n_fragments=%s total_nfev=%s",
                    cfg.experiment_id,
                    len(spfv.get("fragments") or []),
                    sum(
                        int(f.get("nfev", 0))
                        for f in (spfv.get("fragments") or [])
                        if isinstance(f, dict)
                    ),
                )
        if cfg.embedding.dmet_uniform_multifragment_toy:
            labs_mc = [x for x in cfg.embedding.fragment_labels if str(x).strip()]
            if len(labs_mc) >= 2:
                from qchem_stack.integrations.dmet_multifragment_toy import (
                    run_uniform_hamiltonian_multifragment_toy,
                )

                out["dmet_uniform_multifragment_toy"] = run_uniform_hamiltonian_multifragment_toy(
                    cfg, labs_mc, qh, exe, max_cycles=1
                )
        profile.mark("embedding_dmet")
        emit("embedding_dmet")
        return
    if cfg.embedding.mode == "projection":
        emb = cfg.embedding
        wf: dict[str, Any] = {
            "mode": "projection",
            "schema": "projection_embedding_workflow_v1",
            "projection_low_level": emb.projection_low_level,
            "projection_high_level": emb.projection_high_level,
            "projection_threshold": float(emb.projection_threshold),
            "projection_quantum_hamiltonian": emb.projection_quantum_hamiltonian,
            "parity_module": "qchem_stack.chem.embedding.projection",
        }
        hm = out.get("hamiltonian_meta") or {}
        audit = hm.get("projection_mulliken_mo_audit_v1")
        if audit:
            wf["projection_selected_mo_indices"] = list(audit.get("selected_mo_indices") or [])
            wf["projection_mulliken_weights"] = list(audit.get("mulliken_weights") or [])
            wf["projection_integral_source"] = audit.get("integral_source")
        if emb.projection_quantum_hamiltonian == "fragment_mulliken_mo":
            wf["caveat"] = (
                "Main-line VQE uses fragment Mulliken-selected active integrals "
                "(qchem_stack.chem.embedding.projection_hamiltonian)."
            )
            wf["epistemic_bound"] = (
                "Fragment-local MO screening + CASCI active Hamiltonian — not full projection embedding."
            )
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
        return
    if cfg.embedding.mode == "plugin":
        emb = cfg.embedding
        hm = out.get("hamiltonian_meta") or {}
        resolved_json = hm.get("decomposition_plugin_json")
        term_counts = hm.get("decomposition_fragment_pauli_term_counts")
        term_total = 0
        if isinstance(term_counts, dict):
            term_total = sum(int(v) for v in term_counts.values())
        out["embedding_workflow"] = {
            "schema": "embedding_workflow_v1",
            "mode": "plugin",
            "decomposition_plugin": emb.decomposition_plugin,
            "decomposition_plugin_json_path": emb.decomposition_plugin_json_path,
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
        return
    out["embedding_workflow"] = {
        "schema": "embedding_workflow_v1",
        "mode": "none",
        "note": "No DMET/projection embedding stage; variational Hamiltonian uses global active space.",
    }
    if embedding_input_payload is not None:
        out["embedding_workflow"]["embedding_input_system"] = embedding_input_payload
    profile.mark("embedding_none")
    emit("embedding_none")


def _run_excited_stages(
    cfg: ExperimentConfig,
    *,
    qh: QubitHamiltonian,
    exe: Any,
    angles: Any,
    energy_pre: float,
    out: dict[str, Any],
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> dict[str, Any] | None:
    q = cfg.quantum
    ang = np.asarray(angles, dtype=float)
    if q.vqd_after_variational:
        prepare_state = None
        n_vp: int | None = None
        param_bounds: list[tuple[float, float]] | None = None
        if q.variational_ansatz == "uccsd":
            from qchem_stack.quantum.algorithms.uccsd_vqe import UCCSDVQE, UCCSDTrotterVQE

            if q.uccsd_trotter_steps is not None:
                ucc = UCCSDTrotterVQE(
                    qh,
                    executor=exe,
                    n_trotter_steps=int(q.uccsd_trotter_steps),
                )
            else:
                ucc = UCCSDVQE(qh, executor=exe)
            prepare_state = ucc.prepare_state
            n_vp = int(ucc.n_params)
            param_bounds = [(-4.0 * np.pi, 4.0 * np.pi)] * n_vp
        vqd = VQD(
            qh,
            n_states=q.vqd_n_states,
            depth=q.vqe_depth,
            penalty_weight=q.vqd_penalty_weight,
            penalty_weights=q.vqd_penalty_weights,
            overlap_exponent=q.vqd_overlap_exponent,
            cobyla_maxiter=q.vqd_cobyla_maxiter,
            optimizer_method=q.vqd_optimizer_method,
            prepare_state=prepare_state,
            n_var_parameters=n_vp,
            parameter_bounds=param_bounds,
            init_strategy=q.vqd_init_strategy,
            init_noise_scale=q.vqd_init_noise_scale,
            max_overlap_warn=q.vqd_max_overlap_warn,
            overlap_mode=q.vqd_overlap_mode,
            executor=exe,
        )
        vqd_res = vqd.run(
            seed=cfg.random_seed,
            shots_objective=q.vqd_shots_objective,
            shots_overlap=q.vqd_shots_overlap,
            shots_weight=q.vqd_shots_weight,
            pauli_grouping=q.pauli_grouping,
            ground_angles=ang,
            ground_energy=float(energy_pre),
        )
        out["vqd"] = {
            "schema": "excited_vqd_bundle_v1",
            "energies": vqd_res.energies,
            "meta": vqd_res.meta,
        }
    if q.qse_after_variational:
        qse = QSE(qh, subspace_dim=q.qse_subspace_dim)
        kb = q.qse_max_basis
        if q.qse_shot_mode == "exact":
            qse_res = qse.run_from_vqe_hea_basis(ang, q.vqe_depth, max_basis=kb)
        elif q.qse_shot_mode == "gaussian_h":
            qse_res = qse.run_from_vqe_hea_basis_shot_noise(
                ang,
                q.vqe_depth,
                max_basis=kb,
                shots_per_matrix_element=q.qse_shots_per_matrix_element,
                seed=cfg.random_seed,
            )
        else:
            qse_res = qse.run_from_vqe_hea_basis_pauli_transitions(
                ang,
                q.vqe_depth,
                max_basis=kb,
                shots_per_ij_term=q.qse_shots_per_ij_term,
                seed=cfg.random_seed,
            )
        qse_meta = dict(qse_res.meta)
        qse_meta["qse_shot_mode"] = q.qse_shot_mode
        out["qse"] = {
            "schema": "excited_qse_bundle_v1",
            "excitation_energies": qse_res.excitation_energies,
            "meta": qse_meta,
        }
    if q.sceom_after_variational:
        from qchem_stack.quantum.algorithms.sceom import (
            resolve_sceom_s_generators,
            run_sceom_nested_commutator_from_hea,
        )

        sceom_kw: dict[str, Any] = {}
        gens, _ = resolve_sceom_s_generators(
            strategy=q.sceom_generator_strategy,
            hamiltonian=qh,
            subspace_dim=q.sceom_subspace_dim,
        )
        if gens is not None:
            sceom_kw["s_generators"] = gens
        sceom_kw["generator_strategy_yaml"] = q.sceom_generator_strategy
        sceom_res = run_sceom_nested_commutator_from_hea(
            qh,
            ang,
            q.vqe_depth,
            subspace_dim=q.sceom_subspace_dim,
            shots_per_matrix_element=q.sceom_shots_per_matrix_element,
            seed=cfg.random_seed,
            **sceom_kw,
        )
        out["sceom"] = {
            "schema": "excited_sceom_bundle_v1",
            "energies": sceom_res.energies,
            "meta": sceom_res.meta,
        }
    excited_rs = _build_excited_resource_summary(cfg, out)
    if excited_rs is not None:
        out["excited_resource_summary"] = excited_rs
    profile.mark("excited_stages")
    emit("excited_stages")
    return excited_rs


def _run_protocol_and_finalize_stage(
    cfg: ExperimentConfig,
    *,
    out: dict[str, Any],
    qh: QubitHamiltonian,
    angles: Any,
    excited_rs: dict[str, Any] | None,
    bspec: Any,
    exe: Any,
    bundle: Any,
    rhf: ClassicalMeanFieldReference,
    cfg_path: Path | None,
    profile: PipelineStageTimer,
    emit: Callable[[str], None],
) -> dict[str, Any]:
    q = cfg.quantum
    profile.mark("pre_pauli_protocol")
    emit("pre_pauli_protocol")
    if not q.use_pauli_protocol:
        if excited_rs is not None:
            out["resource_summary"] = _resource_summary_excited_only(qh.n_qubits, excited_rs)
        else:
            out["resource_summary"] = {
                "n_circuits": 0,
                "sum_shots": 0,
                "max_depth": 0,
                "sum_twoq": 0,
                "n_qubits": qh.n_qubits,
                "n_pauli_terms": None,
                "n_pauli_groups": None,
                "pauli_averaging_protocol_ran": False,
            }
        _attach_nexus_mitigation_tn(out, cfg, qh)
        _attach_qpe_demo_track_if_requested(out, cfg, qh)
        _attach_qpe_three_algorithm_pack_if_requested(out, cfg, qh)
        _attach_vqs_track_if_requested(out, cfg, qh)
        _finalize_open_stack_parity_snapshot(out, cfg, None)
        _maybe_attach_md_ml_qmef_dataset(out, cfg, rhf, cfg_path=cfg_path)
        profile.mark("pauli_protocol_skipped")
        emit("pauli_protocol_skipped")
        profile.mark("finalize_repro")
        emit("finalize_repro")
        out["repro"]["pipeline_profile"] = profile.to_profile_dict()
        _attach_run_summary(out, cfg)
        return out
    proto = _protocol_for_job(cfg, qh, bspec=bspec, exe=exe, bundle=bundle)
    proto.build(np.asarray(angles, dtype=float), hea_depth=q.vqe_depth)
    proto.compile()
    proto.run()
    e_proto = proto.evaluate()
    rows = proto.dataframe_circuit_shot_rows()
    df_sum = summarize_circuit_shot_rows(rows)
    pc = proto._counts
    resource_summary = {
        **df_sum,
        "n_pauli_terms": pc.get("n_pauli_terms"),
        "n_pauli_groups": pc.get("n_pauli_groups"),
        "pauli_averaging_protocol_ran": True,
    }
    if excited_rs is not None:
        resource_summary["excited_stages"] = excited_rs
        ub = _excited_shots_upper_bound(excited_rs)
        resource_summary["excited_shots_upper_bound"] = ub
        resource_summary["sum_shots_total_with_excited_upper_bound"] = int(df_sum["sum_shots"]) + ub
        if isinstance(excited_rs.get("shot_channel_upper_bounds"), dict):
            resource_summary["excited_shot_accounting"] = excited_rs["shot_channel_upper_bounds"]
        resource_summary["excited_methods_unified"] = _excited_methods_unified(excited_rs)
    out.update(
        {
            "energy_pauli_protocol": float(e_proto),
            "protocol_counts": proto._counts,
            "resource_rows": rows,
            "pauli_measurement_ledger": rows,
            "resource_summary": resource_summary,
        }
    )
    _attach_nexus_mitigation_tn(out, cfg, qh)
    _attach_qpe_demo_track_if_requested(out, cfg, qh)
    _attach_qpe_three_algorithm_pack_if_requested(out, cfg, qh)
    _attach_vqs_track_if_requested(out, cfg, qh)
    _finalize_open_stack_parity_snapshot(out, cfg, proto)
    _maybe_attach_md_ml_qmef_dataset(out, cfg, rhf, cfg_path=cfg_path)
    profile.mark("pauli_protocol_done")
    emit("pauli_protocol_done")
    profile.mark("finalize_repro")
    emit("finalize_repro")
    out["repro"]["pipeline_profile"] = profile.to_profile_dict()
    _attach_run_summary(out, cfg)
    return out


def _classical_benchmark_summary(cb: dict[str, Any]) -> dict[str, Any]:
    return _classical_benchmark_summary_impl(cb)


def _attach_run_summary(out: dict[str, Any], cfg: ExperimentConfig) -> None:
    _attach_run_summary_impl(out, cfg)


def run_pipeline_sync(
    cfg: ExperimentConfig,
    *,
    cfg_path: Path | None = None,
    hamiltonian_out: list[QubitHamiltonian] | None = None,
    run_context: RunContext | None = None,
    job_timeline_emit: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Run chemistry + VQE/ADAPT + optional VQD/QSE/SCEOM + optional Pauli protocol in-process.

    On completion, ``out['repro']['run_summary']`` lists ``stages_completed`` and merges
    resource / protocol semantics for a single JSON reproducibility blob.

    If ``hamiltonian_out`` is an empty list, it is replaced in-place with ``[qh]`` so callers
    (e.g. :func:`run_pipeline_from_config`) can reuse the Hamiltonian without a second PySCF pass.

    ``job_timeline_emit``: optional sink for async job consoles (e.g. ``SqliteJobStore.append_timeline_event``);
    each payload includes ``kind`` (e.g. ``pipeline_stage``), ``stage`` (pipeline segment name), and ``status``.

    Logging: enable the ``qchem_stack.orchestration.pipeline`` logger at INFO for stage milestones
    (SCF, Hamiltonian build, variational energy, optional Schmidt per-fragment VQE) suitable for
    production job tracing.
    """
    cfg = _normalize_precomputed_bundle_path(cfg, cfg_path=cfg_path)
    q = cfg.quantum
    profile = PipelineStageTimer()

    def _emit(stage: str) -> None:
        if job_timeline_emit is not None:
            job_timeline_emit(
                {"kind": "pipeline_stage", "stage": stage, "status": "RUNNING"},
            )

    scf_stage = run_scf_stage(
        cfg,
        profile=profile,
        emit=_emit,
        logger=_pipeline_log,
        context=ScfStageContext(
            is_precomputed_driver_fn=_is_precomputed_driver,
            solver_capabilities_fn=solver_capabilities,
            run_scf_fn=run_scf_reference,
            refine_active_space_fn=refine_mean_field_for_active_space,
            embedding_input_payload_fn=embedding_input_system_payload,
        ),
    )
    cfg = scf_stage.cfg
    rhf = scf_stage.rhf
    pre_q_stage = build_pre_quantum_stage(
        cfg,
        rhf,
        cfg_path=cfg_path,
        profile=profile,
        emit=_emit,
        logger=_pipeline_log,
        context=PreQuantumStageContext(
            is_precomputed_driver_fn=_is_precomputed_driver,
            precomputed_pre_quantum_input_fn=lambda c, r, p: _precomputed_pre_quantum_input(
                c, r, cfg_path=p
            ),
            hamiltonian_with_context_fn=lambda c, r, p: _hamiltonian_with_schmidt_context(
                c, r, cfg_path=p
            ),
        ),
    )
    pre_q_input = pre_q_stage.pre_quantum_input
    schmidt_ctx = pre_q_stage.schmidt_ctx
    qh = pre_q_stage.qh
    energy_components = scf_stage.energy_components
    embedding_input_payload = scf_stage.embedding_input_payload
    classical_benchmarks = scf_stage.classical_benchmarks
    rdm_bundle_meta = scf_stage.rdm_bundle_meta
    rdm_correction_report = scf_stage.rdm_correction_report
    rdm_correction_readiness = scf_stage.rdm_correction_readiness
    if hamiltonian_out is not None:
        hamiltonian_out.clear()
        hamiltonian_out.append(qh)
    repro = collect_repro_metadata(cfg, cfg_path, qh)
    if run_context is not None:
        repro["run_context"] = run_context.to_repro_dict()
    bspec = backend_spec_from_config(cfg)
    exe = executor_from_spec(bspec)
    bundle = compiler_pass_bundle_from_config(cfg)

    vctx = VariationalRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=exe,
        seed=cfg.random_seed,
        pre_quantum_input=pre_q_input,
    )
    stage = run_variational_stage(vctx)
    algo_meta = stage.algo_meta_must_include_algorithm(cfg.quantum.algorithm)
    angles = stage.angles
    energy_pre = float(stage.energy)

    profile.mark("variational_done")
    _emit("variational_done")

    _pipeline_log.info(
        "pipeline variational_done experiment_id=%s algorithm=%s E_var_au=%.10f",
        cfg.experiment_id,
        q.algorithm,
        float(energy_pre),
    )

    out: dict[str, Any] = {
        "repro": repro,
        "scf_energy": float(rhf.e_tot),
        "energy_after_variational": float(energy_pre),
        "angles": angles.tolist() if isinstance(angles, np.ndarray) else list(angles),
        **algo_meta,
    }
    out["pre_quantum_input"] = pre_q_input.as_summary_dict()
    if classical_benchmarks is not None:
        out["classical_benchmarks"] = classical_benchmarks
        out["classical_benchmark_summary"] = _classical_benchmark_summary(classical_benchmarks)
    if embedding_input_payload is not None:
        out["embedding_input_system"] = embedding_input_payload
    out["energy_components"] = energy_components
    if rdm_bundle_meta is not None:
        out["rdm_bundle_meta"] = rdm_bundle_meta
    if rdm_correction_report is not None:
        out["rdm_correction"] = rdm_correction_report
    if rdm_correction_readiness is not None:
        out["rdm_correction_readiness"] = rdm_correction_readiness
    out["hamiltonian_meta"] = dict(qh.meta)
    _apply_embedding_workflow_stage(
        cfg,
        out=out,
        qh=qh,
        exe=exe,
        embedding_input_payload=embedding_input_payload,
        schmidt_ctx=schmidt_ctx,
        rhf=rhf,
        cfg_path=cfg_path,
        profile=profile,
        emit=_emit,
    )
    excited_rs = _run_excited_stages(
        cfg,
        qh=qh,
        exe=exe,
        angles=angles,
        energy_pre=float(energy_pre),
        out=out,
        profile=profile,
        emit=_emit,
    )

    return _run_protocol_and_finalize_stage(
        cfg,
        out=out,
        qh=qh,
        angles=angles,
        excited_rs=excited_rs,
        bspec=bspec,
        exe=exe,
        bundle=bundle,
        rhf=rhf,
        cfg_path=cfg_path,
        profile=profile,
        emit=_emit,
    )


def _protocol_for_job(
    cfg: ExperimentConfig,
    qh: QubitHamiltonian,
    *,
    bspec: Any,
    exe: Any,
    bundle: Any,
) -> PauliAveragingProtocol:
    q = cfg.quantum
    pmsv = None
    if cfg.mitigation.pmsv_enabled:
        pmsv = PMSVConfig(
            stabilizers=list(cfg.mitigation.pmsv_stabilizers),
            retention_rate=float(cfg.mitigation.pmsv_retention_rate),
            report_extension=str(cfg.mitigation.pmsv_report_extension),
            extra=dict(cfg.mitigation.pmsv_extra),
        )
    return PauliAveragingProtocol(
        hamiltonian=qh.operator,
        n_qubits=qh.n_qubits,
        backend=bspec,
        pass_bundle=bundle,
        pmsv=pmsv,
        zne_scales=[float(s) for s in cfg.mitigation.zne_scales]
        if cfg.mitigation.zne_enabled
        else None,
        zne_mode=cfg.mitigation.zne_mode,
        measurement_grouping=q.pauli_grouping,
        run_sampled=q.run_sampled_pauli_protocol,
        run_qiskit_shots=q.run_qiskit_shots_pauli_protocol,
        record_histograms=q.record_pauli_measurement_histograms,
        executor=exe,
        nexus_analog=cfg.nexus_analog,
        pauli_support_max_terms=q.pauli_support_max_terms,
    )


def run_pipeline_from_config(
    cfg_path: str | Path,
    *,
    job_db: Path | None = None,
    enqueue_only: bool = False,
    run_context: RunContext | None = None,
) -> dict[str, Any]:
    """Sync pipeline plus optional job enqueue (pickled :class:`PauliAveragingProtocol`)."""
    p = Path(cfg_path)
    cfg = load_experiment_config(p)
    qh_lane: list[QubitHamiltonian] = []
    sync = run_pipeline_sync(cfg, cfg_path=p, hamiltonian_out=qh_lane, run_context=run_context)

    if job_db is None or not cfg.quantum.use_pauli_protocol:
        return sync

    qh = qh_lane[0]
    angles = np.asarray(sync["angles"], dtype=float)
    bspec2 = backend_spec_from_config(cfg)
    exe2 = executor_from_spec(bspec2)
    bundle2 = compiler_pass_bundle_from_config(cfg)
    proto = _protocol_for_job(cfg, qh, bspec=bspec2, exe=exe2, bundle=bundle2)
    proto.build(angles, hea_depth=cfg.quantum.vqe_depth)
    proto.compile()
    blob = proto.dumps()
    ph = hashlib.sha256(blob).hexdigest()[:24]
    store = SqliteJobStore(job_db)
    handle = proto.launch(store)
    sync["job"] = {"job_id": handle.job_id, "protocol_hash": ph, "store": str(job_db)}
    if not enqueue_only:
        PauliAveragingProtocol.process_job(store, handle.job_id)
        sync["job_result"] = store.result(handle.job_id)
    _attach_run_summary(sync, cfg)
    return sync

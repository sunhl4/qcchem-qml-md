"""Pauli protocol finalize stage and optional attachment sidecars."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np

from qchem_stack.backends.spec import summarize_circuit_shot_rows
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import ExperimentConfig, backend_spec_from_config
from qchem_stack.jobs.nexus_analog import nexus_analog_ledger_from_rows
from qchem_stack.jobs.nexus_cloud import nexus_cloud_repro_sidecar
from qchem_stack.mitigation.pmsv import PMSVConfig
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.mitigation.qermit_runtime import execute_mitigation_dag_runtime
from qchem_stack.orchestration.excited_stages import (
    build_excited_resource_summary,
    excited_methods_unified,
    excited_shots_upper_bound,
)
from qchem_stack.orchestration.parity_finalize import finalize_open_stack_parity_snapshot
from qchem_stack.orchestration.repro_summary import attach_run_summary as attach_run_summary_impl
from qchem_stack.orchestration.run_context import PipelineStageTimer
from qchem_stack.protocols.protocol import PauliAveragingProtocol

def attach_nexus_mitigation_tn(
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


def attach_qpe_demo_track_if_requested(
    out: dict[str, Any], cfg: ExperimentConfig, qh: QubitHamiltonian
) -> None:
    """Optional dense QPE + Bayesian toy, same as ``scripts/run_qpe_track_demo.py`` (NISQ + FT narrative)."""
    if not cfg.quantum.qpe_demo_track_requested():
        return
    from qchem_stack.qpe_qec_demo.pipeline_track import qpe_demo_track_payload

    out["qpe_demo_track"] = qpe_demo_track_payload(qh, bits=int(cfg.quantum.qpe_demo_track_n_bits))


def attach_vqs_track_if_requested(
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


def attach_qpe_three_algorithm_pack_if_requested(
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


def resource_summary_excited_only(n_qubits: int, excited_rs: dict[str, Any]) -> dict[str, Any]:
    ub = excited_shots_upper_bound(excited_rs)
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
    rs["excited_methods_unified"] = excited_methods_unified(excited_rs)
    return rs


def maybe_attach_md_ml_qmef_dataset(
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



def run_protocol_and_finalize_stage(
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
            out["resource_summary"] = resource_summary_excited_only(qh.n_qubits, excited_rs)
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
        attach_nexus_mitigation_tn(out, cfg, qh)
        attach_qpe_demo_track_if_requested(out, cfg, qh)
        attach_qpe_three_algorithm_pack_if_requested(out, cfg, qh)
        attach_vqs_track_if_requested(out, cfg, qh)
        finalize_open_stack_parity_snapshot(out, cfg, None)
        maybe_attach_md_ml_qmef_dataset(out, cfg, rhf, cfg_path=cfg_path)
        profile.mark("pauli_protocol_skipped")
        emit("pauli_protocol_skipped")
        profile.mark("finalize_repro")
        emit("finalize_repro")
        out["repro"]["pipeline_profile"] = profile.to_profile_dict()
        attach_run_summary_impl(out, cfg)
        return out
    proto = protocol_for_job(cfg, qh, bspec=bspec, exe=exe, bundle=bundle)
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
        ub = excited_shots_upper_bound(excited_rs)
        resource_summary["excited_shots_upper_bound"] = ub
        resource_summary["sum_shots_total_with_excited_upper_bound"] = int(df_sum["sum_shots"]) + ub
        if isinstance(excited_rs.get("shot_channel_upper_bounds"), dict):
            resource_summary["excited_shot_accounting"] = excited_rs["shot_channel_upper_bounds"]
        resource_summary["excited_methods_unified"] = excited_methods_unified(excited_rs)
    out.update(
        {
            "energy_pauli_protocol": float(e_proto),
            "protocol_counts": proto._counts,
            "resource_rows": rows,
            "pauli_measurement_ledger": rows,
            "resource_summary": resource_summary,
        }
    )
    attach_nexus_mitigation_tn(out, cfg, qh)
    attach_qpe_demo_track_if_requested(out, cfg, qh)
    attach_qpe_three_algorithm_pack_if_requested(out, cfg, qh)
    attach_vqs_track_if_requested(out, cfg, qh)
    finalize_open_stack_parity_snapshot(out, cfg, proto)
    maybe_attach_md_ml_qmef_dataset(out, cfg, rhf, cfg_path=cfg_path)
    profile.mark("pauli_protocol_done")
    emit("pauli_protocol_done")
    profile.mark("finalize_repro")
    emit("finalize_repro")
    out["repro"]["pipeline_profile"] = profile.to_profile_dict()
    attach_run_summary_impl(out, cfg)
    return out



def protocol_for_job(
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

